from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import text

from .. import db
from ..forms import TransactionForm
from ..models import Portfolio, Product, Customer, Employee

bp = Blueprint("transactions", __name__, url_prefix="/trade")


@bp.route("/create", methods=["GET", "POST"])
def create_trade():
    form = TransactionForm()
    portfolios = Portfolio.query.order_by(Portfolio.portfolio_name.asc()).all()
    products = Product.query.order_by(Product.product_name.asc()).all()
    customers = Customer.query.order_by(Customer.first_name.asc(), Customer.last_name.asc()).all()
    employees = Employee.query.order_by(Employee.employee_name.asc()).all()
    form.user.choices = [
        (f"C:{c.c_id}", f"Client: {c.first_name} {c.last_name}") for c in customers
    ] + [
        (f"E:{e.e_id}", f"Employee: {e.employee_name}") for e in employees
    ]
    form.p_id.choices = [(p.p_id, f"{p.portfolio_name}") for p in portfolios]
    form.product_id.choices = [
        (p.product_id, f"{p.product_name} ({p.ticker_symbol or 'No Ticker'})") for p in products
    ]

    if form.validate_on_submit():
        # Call stored procedure Process_Trade(P_ID, Product_ID, quantity, price_per_unit, commission_rate)
        try:
            # Commission by user type: Employees 10%, Clients 20%
            selected_user = form.user.data or ""
            comm_float = 0.10 if selected_user.startswith("E:") else 0.20

            # Default price per unit from product if not provided
            ppu_input = form.price_per_unit.data
            if ppu_input is None:
                prod = db.session.get(Product, form.product_id.data)
                ppu_input = prod.current_price if prod and prod.current_price is not None else 0

            db.session.execute(
                text("CALL Process_Trade(:p_id, :product_id, :qty, :ppu, :comm)"),
                {
                    "p_id": form.p_id.data,
                    "product_id": form.product_id.data,
                    "qty": form.quantity.data,
                    "ppu": ppu_input,
                    "comm": comm_float,
                },
            )
            db.session.commit()
            flash("Trade submitted successfully.", "success")
            return redirect(url_for("transactions.create_trade"))
        except Exception as exc:
            db.session.rollback()
            flash(f"Error executing trade: {exc}", "danger")

    # Provide product->price map and initial commission for UI auto-fill
    price_map = {p.product_id: (float(p.current_price) if p.current_price is not None else None) for p in products}
    return render_template("transactions/create.html", form=form, price_map=price_map)


