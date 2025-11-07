from __future__ import annotations

from typing import Any, List

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import text
from werkzeug.exceptions import NotFound

from .. import db
from ..forms import CustomerForm, CustomerDetailsForm
from ..models import Customer, CustomerDetails, CustomerPhone, CustomerEmail

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.get("/")
def list_customers():
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    col_map = {
        "id": [Customer.c_id],
        "name": [Customer.first_name, Customer.last_name],
        "dob": [Customer.date_of_birth],
    }
    cols = col_map.get(sort, col_map["id"])  # default to id
    order_by = [c.desc() if order == "desc" else c.asc() for c in cols]

    customers = Customer.query.order_by(*order_by).all()
    return render_template(
        "customers/list.html",
        customers=customers,
        sort=sort,
        order=order,
    )


@bp.route("/create", methods=["GET", "POST"])
def create_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
        )
        db.session.add(customer)
        db.session.commit()
        flash("Customer created. Please complete KYC & Contacts.", "success")
        return redirect(url_for("customers.details", c_id=customer.c_id))
    return render_template("customers/create.html", form=form)


@bp.route("/<int:c_id>/details", methods=["GET", "POST"])
def details(c_id: int):
    customer = Customer.query.get(c_id)
    if customer is None:
        raise NotFound()

    form = CustomerDetailsForm()

    if request.method == "GET":
        # If details exist, preload one phone/email entry; otherwise leave defaults
        if customer.details:
            form.ssn.data = customer.details.ssn
            form.pan_number.data = customer.details.pan_number
            form.aadhar_number.data = customer.details.aadhar_number
            form.occupation.data = customer.details.occupation
            if customer.details.annual_income is not None:
                form.annual_income.data = float(customer.details.annual_income)
            form.risk_tolerance.data = customer.details.risk_tolerance
        # Populate existing phones/emails into the first entries if present
        phones = customer.phones
        emails = customer.emails
        if phones:
            form.phones.pop_entry()
            for ph in phones:
                entry = {}
                entry_form = {}
                form.phones.append_entry({
                    "phone_number": ph.phone_number,
                    "phone_type": ph.phone_type or "",
                })
        if emails:
            form.emails.pop_entry()
            for em in emails:
                form.emails.append_entry({
                    "email_address": em.email_address,
                    "email_type": em.email_type or "",
                })

    if form.validate_on_submit():
        # Unique checks for aadhar/pan/ssn across other customers; use no_autoflush to avoid premature flush
        with db.session.no_autoflush:
            if db.session.scalar(
                db.select(CustomerDetails).where(
                    CustomerDetails.aadhar_number == form.aadhar_number.data,
                    CustomerDetails.c_id != c_id,
                )
            ):
                flash("Aadhar Number already exists for another customer.", "danger")
                return render_template("customers/details.html", form=form, customer=customer)
            if form.ssn.data and db.session.scalar(
                db.select(CustomerDetails).where(
                    CustomerDetails.ssn == form.ssn.data,
                    CustomerDetails.c_id != c_id,
                )
            ):
                flash("SSN already exists for another customer.", "danger")
                return render_template("customers/details.html", form=form, customer=customer)
            if db.session.scalar(
                db.select(CustomerDetails).where(
                    CustomerDetails.pan_number == form.pan_number.data,
                    CustomerDetails.c_id != c_id,
                )
            ):
                flash("PAN Number already exists for another customer.", "danger")
                return render_template("customers/details.html", form=form, customer=customer)

            # Upsert details
            details = customer.details or CustomerDetails(c_id=customer.c_id)
            details.ssn = form.ssn.data or None
            details.pan_number = form.pan_number.data
            details.aadhar_number = form.aadhar_number.data
            details.occupation = form.occupation.data
            details.annual_income = (
                form.annual_income.data if form.annual_income.data is not None else None
            )
            details.risk_tolerance = form.risk_tolerance.data if form.risk_tolerance.data else None
            customer.details = details

            # Phones: replace with submitted list (phones have no uniqueness constraints)
            customer.phones.clear()
            for entry in form.phones.entries:
                if entry.form.phone_number.data:
                    customer.phones.append(
                        CustomerPhone(
                            phone_number=entry.form.phone_number.data,
                            phone_type=entry.form.phone_type.data or None,
                        )
                    )

            # Emails: upsert per address to avoid unique constraint clashes during autoflush
            submitted_emails = []
            for entry in form.emails.entries:
                addr = entry.form.email_address.data.strip() if entry.form.email_address.data else ""
                etype = entry.form.email_type.data or None
                if addr:
                    submitted_emails.append((addr, etype))

            # Check duplicates within submitted
            seen = set()
            dup_in_form = {addr for addr, _ in submitted_emails if (addr in seen or seen.add(addr))}
            if dup_in_form:
                flash("Duplicate email addresses in form: " + ", ".join(sorted(dup_in_form)), "danger")
                return render_template("customers/details.html", form=form, customer=customer)

            existing_by_addr = {em.email_address: em for em in list(customer.emails)}

            # Delete removed
            to_keep = {addr for addr, _ in submitted_emails}
            for addr, em in existing_by_addr.items():
                if addr not in to_keep:
                    db.session.delete(em)

            # Validate global uniqueness for new emails (addresses not already belonging to this customer)
            to_add = [addr for addr, _ in submitted_emails if addr not in existing_by_addr]
            if to_add:
                existing_conflicts = db.session.execute(
                    db.select(CustomerEmail.email_address).where(
                        CustomerEmail.email_address.in_(to_add),
                        CustomerEmail.c_id != customer.c_id,
                    )
                ).scalars().all()
                if existing_conflicts:
                    flash(
                        "Email(s) already exist for another customer: " + ", ".join(sorted(existing_conflicts)),
                        "danger",
                    )
                    return render_template("customers/details.html", form=form, customer=customer)

            # Update existing types; add new ones
            for addr, etype in submitted_emails:
                if addr in existing_by_addr:
                    existing_by_addr[addr].email_type = etype
                else:
                    customer.emails.append(
                        CustomerEmail(email_address=addr, email_type=etype)
                    )

        db.session.add(customer)
        db.session.commit()
        flash("KYC & Contacts saved.", "success")
        return redirect(url_for("customers.view", c_id=customer.c_id))

    return render_template("customers/details.html", form=form, customer=customer)


@bp.get("/<int:c_id>")
def view(c_id: int):
    customer = Customer.query.get(c_id)
    if customer is None:
        raise NotFound()

    # Calculate age via DB function Calculate_Age(dob DATE)
    age_years: int | None = None
    if customer.date_of_birth:
        try:
            result = db.session.execute(
                text("SELECT Calculate_Age(:dob) AS age"), {"dob": customer.date_of_birth}
            ).first()
            if result is not None:
                age_years = int(result.age) if result.age is not None else None
        except Exception as exc:
            # Non-fatal: show no age if function missing
            age_years = None

    # Total net worth: SUM(quantity * price_per_unit) across customer's portfolios
    net_worth = 0.0
    try:
        nw_row = db.session.execute(
            text(
                """
                SELECT COALESCE(SUM(t.quantity * t.price_per_unit), 0) AS net_worth
                FROM transactions t
                JOIN portfolios p ON t.P_ID = p.P_ID
                WHERE p.C_ID = :cid
                """
            ),
            {"cid": customer.c_id},
        ).first()
        if nw_row is not None and nw_row.net_worth is not None:
            net_worth = float(nw_row.net_worth)
    except Exception:
        net_worth = 0.0

    # Per-portfolio products summary
    portfolios = (
        db.session.query(Customer).get(customer.c_id).portfolios  # use relationship
    )
    portfolio_products: list[dict[str, object]] = []
    for p in portfolios:
        rows = db.session.execute(
            text(
                """
                SELECT pr.Product_name AS product_name,
                       pr.ticker_symbol AS ticker,
                       SUM(t.quantity) AS total_qty,
                       SUM(t.quantity * t.price_per_unit) AS invested
                FROM transactions t
                JOIN products pr ON pr.Product_ID = t.Product_ID
                WHERE t.P_ID = :pid
                GROUP BY pr.Product_ID, pr.Product_name, pr.ticker_symbol
                ORDER BY invested DESC
                """
            ),
            {"pid": p.p_id},
        ).mappings().all()
        portfolio_products.append({
            "portfolio": p,
            "products": rows,
        })

    return render_template(
        "customers/view.html",
        customer=customer,
        age_years=age_years,
        net_worth=net_worth,
        portfolio_products=portfolio_products,
    )


