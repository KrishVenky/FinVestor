"""Helper script to create an employee in the database.

Usage:
    python scripts/create_employee.py <employee_name> [job_title] [hire_date]

Examples:
    python scripts/create_employee.py "John Admin" "Administrator" "2024-01-01"
    python scripts/create_employee.py "Jane Manager"
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from datetime import date

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
from app.models import Employee


def create_employee(employee_name: str, job_title: str | None = None, hire_date: str | None = None) -> None:
    """Create a new employee."""
    app = create_app()
    
    with app.app_context():
        # Parse hire_date if provided
        hire_date_obj = None
        if hire_date:
            try:
                hire_date_obj = date.fromisoformat(hire_date)
            except ValueError:
                print(f"Error: Invalid date format '{hire_date}'. Use YYYY-MM-DD format.")
                return
        
        # Create employee
        employee = Employee(
            employee_name=employee_name,
            job_title=job_title,
            hire_date=hire_date_obj,
            specialization=None,  # Trigger will set to 'General Support' if NULL
            manager_id=None
        )
        
        db.session.add(employee)
        db.session.commit()
        
        print(f"Successfully created employee '{employee_name}' with ID {employee.e_id}")
        print(f"You can now create a user account linked to this employee:")
        print(f"  python scripts/create_user.py <username> <password> <role> {employee.e_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    employee_name = sys.argv[1]
    job_title = sys.argv[2] if len(sys.argv) > 2 else None
    hire_date = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_employee(employee_name, job_title, hire_date)

