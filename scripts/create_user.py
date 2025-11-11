"""Helper script to create users for testing authentication.

Usage:
    python scripts/create_user.py <username> <password> <role> [customer_id|employee_id]

Examples:
    # Create a regular customer user
    python scripts/create_user.py john_doe password123 regular 1

    # Create an employee user
    python scripts/create_user.py jane_smith password123 employee 1

    # Create a manager user (must be linked to an employee)
    python scripts/create_user.py manager1 password123 manager 1

    # Create a superadmin user (must be linked to an employee)
    python scripts/create_user.py admin password123 superadmin 1
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    print("Warning: .env file not found. Make sure your database credentials are set in environment variables.")

from app import create_app, db
from app.models import User, Customer, Employee


def create_user(username: str, password: str, role: str, entity_id: int | None = None) -> None:
    """Create a new user account."""
    app = create_app()
    
    with app.app_context():
        # Validate role
        valid_roles = ("regular", "employee", "manager", "superadmin")
        if role not in valid_roles:
            print(f"Error: Role must be one of {valid_roles}")
            return
        
        # Check if username already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"Error: Username '{username}' already exists")
            return
        
        # Determine entity type and validate
        c_id = None
        e_id = None
        
        if entity_id is not None:
            if role in ("regular",):
                # Regular users should be linked to customers
                customer = db.session.get(Customer, entity_id)
                if customer is None:
                    print(f"Error: Customer with ID {entity_id} not found")
                    print("\nAvailable customers:")
                    customers = Customer.query.all()
                    if customers:
                        for c in customers:
                            print(f"  ID {c.c_id}: {c.first_name} {c.last_name}")
                    else:
                        print("  No customers found. Create a customer first.")
                    print("\nTo create a customer, use the web interface or SQL.")
                    return
                c_id = entity_id
            else:
                # Employees, managers, and superadmins should be linked to employees
                employee = db.session.get(Employee, entity_id)
                if employee is None:
                    print(f"Error: Employee with ID {entity_id} not found")
                    print("\nAvailable employees:")
                    employees = Employee.query.all()
                    if employees:
                        for e in employees:
                            print(f"  ID {e.e_id}: {e.employee_name} ({e.job_title or 'No title'})")
                    else:
                        print("  No employees found.")
                    print("\nTo create an employee, run:")
                    print(f"  python scripts/create_employee.py \"Employee Name\" \"Job Title\"")
                    return
                e_id = entity_id
        
        # Create user
        user = User(
            username=username,
            role=role,
            c_id=c_id,
            e_id=e_id,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        entity_type = "customer" if c_id else "employee"
        entity_id_val = c_id if c_id else e_id
        print(f"Successfully created user '{username}' with role '{role}' linked to {entity_type} ID {entity_id_val}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3].lower()
    entity_id = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    create_user(username, password, role, entity_id)

