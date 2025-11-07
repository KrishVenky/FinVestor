from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for, request

from .. import db
from ..forms import PortfolioForm
from ..models import Portfolio, Customer, Employee

bp = Blueprint("portfolios", __name__, url_prefix="/portfolios")


@bp.get("/")
def list_portfolios():
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    col_map = {
        "id": [Portfolio.p_id],
        "name": [Portfolio.portfolio_name],
        "customer": [Portfolio.c_id],
        "employee": [Portfolio.e_id],
        "risk": [Portfolio.risk_level],
        "currency": [Portfolio.currency],
    }
    cols = col_map.get(sort, col_map["id"])  # default id
    order_by = [c.desc() if order == "desc" else c.asc() for c in cols]

    portfolios = Portfolio.query.order_by(*order_by).all()
    return render_template("portfolios/list.html", portfolios=portfolios, sort=sort, order=order)


@bp.route("/create", methods=["GET", "POST"])
def create_portfolio():
    form = PortfolioForm()
    customers = Customer.query.order_by(Customer.first_name.asc(), Customer.last_name.asc()).all()
    employees = Employee.query.order_by(Employee.employee_name.asc()).all()
    form.c_id.choices = [(0, "-- None --")] + [(c.c_id, f"{c.first_name} {c.last_name}") for c in customers]
    form.e_id.choices = [(0, "-- None --")] + [(e.e_id, e.employee_name) for e in employees]

    if form.validate_on_submit():
        c_val = form.c_id.data if form.c_id.data != 0 else None
        e_val = form.e_id.data if form.e_id.data != 0 else None
        if c_val is None and e_val is None:
            flash("Select at least one owner: Customer or Employee.", "danger")
            return render_template("portfolios/create.html", form=form)

        portfolio = Portfolio(
            portfolio_name=form.portfolio_name.data,
            c_id=c_val,
            e_id=e_val,
            creation_date=form.creation_date.data,
            risk_level=form.risk_level.data or None,
            currency=form.currency.data or None,
        )
        db.session.add(portfolio)
        db.session.commit()
        flash("Portfolio created.", "success")
        return redirect(url_for("portfolios.list_portfolios"))

    return render_template("portfolios/create.html", form=form)


