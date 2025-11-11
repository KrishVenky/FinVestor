"""User management routes for admins and managers."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import NotFound

from .. import db
from ..auth import login_required, manager_required, get_current_user
from ..forms import UserForm
from ..models import User, Customer, Employee

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("/")
@manager_required
def list_users():
    """List all users - only managers/superadmins."""
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    col_map = {
        "id": [User.user_id],
        "username": [User.username],
        "role": [User.role],
        "entity": [User.c_id, User.e_id],
    }
    cols = col_map.get(sort, col_map["id"])
    order_by = [c.desc() if order == "desc" else c.asc() for c in cols]

    users = User.query.order_by(*order_by).all()
    return render_template("users/list.html", users=users, sort=sort, order=order)


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_user():
    """Create a new user account - only managers/superadmins."""
    form = UserForm()
    
    # Populate entity choices
    customers = Customer.query.order_by(Customer.first_name.asc(), Customer.last_name.asc()).all()
    employees = Employee.query.order_by(Employee.employee_name.asc()).all()
    
    form.c_id.choices = [(0, "-- None --")] + [(c.c_id, f"{c.first_name} {c.last_name}") for c in customers]
    form.e_id.choices = [(0, "-- None --")] + [(e.e_id, e.employee_name) for e in employees]
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        role = form.role.data
        c_id = form.c_id.data if form.c_id.data != 0 else None
        e_id = form.e_id.data if form.e_id.data != 0 else None
        
        # Validate password is provided for new users
        if not password or len(password) < 6:
            flash("Password is required and must be at least 6 characters.", "danger")
            return render_template("users/create.html", form=form)
        
        # Validate at least one entity is selected
        if c_id is None and e_id is None:
            flash("Please select either a Customer or Employee.", "danger")
            return render_template("users/create.html", form=form)
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Please choose a different username.", "danger")
            return render_template("users/create.html", form=form)
        
        # Validate entity exists and check if already linked
        if c_id is not None:
            customer = db.session.get(Customer, c_id)
            if customer is None:
                flash("Selected customer not found.", "danger")
                return render_template("users/create.html", form=form)
            
            existing_link = User.query.filter_by(c_id=c_id).first()
            if existing_link:
                flash(f"Customer ID {c_id} is already linked to user '{existing_link.username}'.", "danger")
                return render_template("users/create.html", form=form)
        
        if e_id is not None:
            employee = db.session.get(Employee, e_id)
            if employee is None:
                flash("Selected employee not found.", "danger")
                return render_template("users/create.html", form=form)
            
            existing_link = User.query.filter_by(e_id=e_id).first()
            if existing_link:
                flash(f"Employee ID {e_id} is already linked to user '{existing_link.username}'.", "danger")
                return render_template("users/create.html", form=form)
        
        # Create user
        user = User(
            username=username,
            role=role,
            c_id=c_id,
            e_id=e_id,
            is_active=form.is_active.data == "True"
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f"User '{username}' created successfully with role '{role}'.", "success")
        return redirect(url_for("users.list_users"))
    
    return render_template("users/create.html", form=form)


@bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_user(user_id: int):
    """Edit user account - only managers/superadmins."""
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFound()
    
    form = UserForm(obj=user)
    form.password.validators = []  # Make password optional for editing
    
    # Populate entity choices
    customers = Customer.query.order_by(Customer.first_name.asc(), Customer.last_name.asc()).all()
    employees = Employee.query.order_by(Employee.employee_name.asc()).all()
    
    form.c_id.choices = [(0, "-- None --")] + [(c.c_id, f"{c.first_name} {c.last_name}") for c in customers]
    form.e_id.choices = [(0, "-- None --")] + [(e.e_id, e.employee_name) for e in employees]
    
    if request.method == "GET":
        form.c_id.data = user.c_id or 0
        form.e_id.data = user.e_id or 0
        form.is_active.data = "True" if user.is_active else "False"
    
    if form.validate_on_submit():
        user.username = form.username.data.strip()
        user.role = form.role.data
        user.is_active = form.is_active.data == "True"
        
        # Update password only if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        # Update entity links
        c_id = form.c_id.data if form.c_id.data != 0 else None
        e_id = form.e_id.data if form.e_id.data != 0 else None
        
        if c_id is None and e_id is None:
            flash("Please select either a Customer or Employee.", "danger")
            return render_template("users/edit.html", form=form, user=user)
        
        # Validate entity exists and check if already linked (excluding current user)
        if c_id is not None and c_id != user.c_id:
            customer = db.session.get(Customer, c_id)
            if customer is None:
                flash("Selected customer not found.", "danger")
                return render_template("users/edit.html", form=form, user=user)
            
            existing_link = User.query.filter(User.c_id == c_id, User.user_id != user_id).first()
            if existing_link:
                flash(f"Customer ID {c_id} is already linked to user '{existing_link.username}'.", "danger")
                return render_template("users/edit.html", form=form, user=user)
        
        if e_id is not None and e_id != user.e_id:
            employee = db.session.get(Employee, e_id)
            if employee is None:
                flash("Selected employee not found.", "danger")
                return render_template("users/edit.html", form=form, user=user)
            
            existing_link = User.query.filter(User.e_id == e_id, User.user_id != user_id).first()
            if existing_link:
                flash(f"Employee ID {e_id} is already linked to user '{existing_link.username}'.", "danger")
                return render_template("users/edit.html", form=form, user=user)
        
        user.c_id = c_id
        user.e_id = e_id
        
        db.session.commit()
        flash(f"User '{user.username}' updated successfully.", "success")
        return redirect(url_for("users.list_users"))
    
    return render_template("users/edit.html", form=form, user=user)


@bp.route("/<int:user_id>/delete", methods=["POST"])
@manager_required
def delete_user(user_id: int):
    """Delete user account - only managers/superadmins."""
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFound()
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User '{username}' deleted successfully.", "success")
    return redirect(url_for("users.list_users"))

