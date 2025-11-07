from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for, request

from .. import db
from ..forms import EmployeeForm
from ..models import Employee

bp = Blueprint("employees", __name__, url_prefix="/employees")


@bp.get("/")
def list_employees():
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

    employees = Employee.query.order_by(*order_by).all()
    return render_template("employees/list.html", employees=employees, sort=sort, order=order)


@bp.route("/create", methods=["GET", "POST"])
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


