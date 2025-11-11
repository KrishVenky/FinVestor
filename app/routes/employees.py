from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for, request
from werkzeug.exceptions import NotFound

from .. import db
from ..auth import login_required, manager_required, get_current_user, can_access_entity
from ..forms import EmployeeForm
from ..models import Employee

bp = Blueprint("employees", __name__, url_prefix="/employees")


@bp.get("/")
@login_required
def list_employees():
    """List employees - managers/superadmins see all, regular users see only themselves."""
    current_user = get_current_user()
    if current_user is None:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("auth.login"))
    
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    col_map = {
        "id": [Employee.e_id],
        "name": [Employee.employee_name],
        "job_title": [Employee.job_title],
        "manager": [Employee.manager_id],
    }
    cols = col_map.get(sort, col_map["id"])  # default id
    order_by = [c.desc() if order == "desc" else c.asc() for c in cols]

    # Managers and superadmins see all employees
    if current_user.can_access_all():
        employees = Employee.query.order_by(*order_by).all()
    else:
        # Regular users/employees see only their own employee record
        if current_user.e_id is not None:
            employees = Employee.query.filter_by(e_id=current_user.e_id).order_by(*order_by).all()
        else:
            employees = []
    
    return render_template("employees/list.html", employees=employees, sort=sort, order=order)


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_employee():
    form = EmployeeForm()
    # Populate manager choices with current employees
    managers = Employee.query.order_by(Employee.employee_name.asc()).all()
    form.manager_id.choices = [(0, "-- None --")] + [(e.e_id, e.employee_name) for e in managers]

    if form.validate_on_submit():
        manager_id_val = form.manager_id.data if form.manager_id.data != 0 else None
        employee = Employee(
            employee_name=form.employee_name.data,
            job_title=form.job_title.data,
            hire_date=form.hire_date.data,
            specialization=form.specialization.data or None,
            manager_id=manager_id_val,
        )
        db.session.add(employee)
        db.session.commit()
        flash("Employee created.", "success")
        return redirect(url_for("employees.list_employees"))

    return render_template("employees/create.html", form=form)


@bp.route("/<int:e_id>/delete", methods=["POST"])
@manager_required
def delete_employee(e_id: int):
    employee = Employee.query.get(e_id)
    if employee is None:
        raise NotFound()
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted successfully.", "success")
    return redirect(url_for("employees.list_employees"))


