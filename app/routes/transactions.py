from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import text

from .. import db
from ..auth import login_required, manager_required, get_current_user
from ..forms import TransactionForm
from ..models import Portfolio, Product, Customer, Employee

bp = Blueprint("transactions", __name__, url_prefix="/trade")


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_trade():
    """Create a trade - managers can trade for anyone, regular users only their own portfolios."""
    current_user = get_current_user()
    if current_user is None:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("auth.login"))
    
    form = TransactionForm()
    
    # Filter portfolios based on user role
    if current_user.can_access_all():
        portfolios = Portfolio.query.order_by(Portfolio.portfolio_name.asc()).all()
        customers = Customer.query.order_by(Customer.first_name.asc(), Customer.last_name.asc()).all()
        employees = Employee.query.order_by(Employee.employee_name.asc()).all()
    else:
        # Regular users can only see their own portfolios
        if current_user.c_id is not None:
            portfolios = Portfolio.query.filter_by(c_id=current_user.c_id).order_by(Portfolio.portfolio_name.asc()).all()
            customers = Customer.query.filter_by(c_id=current_user.c_id).all()
            employees = []
        elif current_user.e_id is not None:
            portfolios = Portfolio.query.filter_by(e_id=current_user.e_id).order_by(Portfolio.portfolio_name.asc()).all()
            customers = []
            employees = Employee.query.filter_by(e_id=current_user.e_id).all()
        else:
            portfolios = []
            customers = []
            employees = []
    
    products = Product.query.order_by(Product.product_name.asc()).all()
    # Only show user selection if manager/superadmin
    if current_user.can_access_all():
        form.user.choices = [
            (f"C:{c.c_id}", f"Customer: {c.first_name} {c.last_name}") for c in customers
        ] + [
            (f"E:{e.e_id}", f"Employee: {e.employee_name}") for e in employees
        ]
    else:
        # Regular users - auto-select their own entity
        if current_user.c_id is not None:
            form.user.choices = [(f"C:{current_user.c_id}", f"Client: {current_user.customer.first_name if current_user.customer else ''} {current_user.customer.last_name if current_user.customer else ''}")]
            form.user.data = f"C:{current_user.c_id}"
        elif current_user.e_id is not None:
            form.user.choices = [(f"E:{current_user.e_id}", f"Employee: {current_user.employee.employee_name if current_user.employee else ''}")]
            form.user.data = f"E:{current_user.e_id}"
        else:
            form.user.choices = []

    # Determine selected user (from POST or querystring) to filter portfolios accordingly
    selected_user_str = form.user.data or None
    if not selected_user_str:
        selected_user_str = None
    filtered_portfolios = portfolios
    if selected_user_str:
        try:
            utype, uid_str = selected_user_str.split(":", 1)
            uid = int(uid_str)
            if utype == "C":
                filtered_portfolios = [p for p in portfolios if p.c_id == uid]
            elif utype == "E":
                filtered_portfolios = [p for p in portfolios if p.e_id == uid]
        except Exception:
            filtered_portfolios = portfolios

    form.p_id.choices = [(p.p_id, f"{p.portfolio_name}") for p in filtered_portfolios]
    form.product_id.choices = [
        (p.product_id, f"{p.product_name} ({p.ticker_symbol or 'No Ticker'})") for p in products
    ]

    if form.validate_on_submit():
        # Call stored procedure Process_Trade(P_ID, Product_ID, quantity, price_per_unit, commission_rate)
        try:
            # Commission by user type: Employees 10%, Customers 20%
            selected_user = form.user.data or ""
            comm_float = 0.10 if selected_user.startswith("E:") else 0.20

            # Validate selected portfolio ownership matches selected user
            portfolio = db.session.get(Portfolio, form.p_id.data)
            if portfolio is None:
                raise ValueError("Invalid portfolio selected")
            
            # For regular users, ensure they can only trade on their own portfolios
            if not current_user.can_access_all():
                if current_user.c_id is not None and portfolio.c_id != current_user.c_id:
                    flash("You can only trade on your own portfolios.", "danger")
                    return render_template("transactions/create.html", form=form, price_map={p.product_id: (float(p.current_price) if p.current_price is not None else None) for p in products})
                elif current_user.e_id is not None and portfolio.e_id != current_user.e_id:
                    flash("You can only trade on your own portfolios.", "danger")
                    return render_template("transactions/create.html", form=form, price_map={p.product_id: (float(p.current_price) if p.current_price is not None else None) for p in products})
            
            # For managers, validate portfolio ownership matches selected user
            if current_user.can_access_all():
                if selected_user.startswith("C:"):
                    sel_id = int(selected_user.split(":", 1)[1])
                    if portfolio.c_id != sel_id:
                        flash("Selected portfolio is not owned by the chosen client.", "danger")
                        return render_template("transactions/create.html", form=form, price_map={p.product_id: (float(p.current_price) if p.current_price is not None else None) for p in products})
                elif selected_user.startswith("E:"):
                    sel_id = int(selected_user.split(":", 1)[1])
                    if portfolio.e_id != sel_id:
                        flash("Selected portfolio is not owned by the chosen employee.", "danger")
                        return render_template("transactions/create.html", form=form, price_map={p.product_id: (float(p.current_price) if p.current_price is not None else None) for p in products})

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


