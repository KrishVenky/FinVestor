from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for, request
from werkzeug.exceptions import NotFound

from .. import db
from ..auth import login_required, manager_required
from ..forms import ProductForm
from ..models import Product

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.get("/")
@login_required
def list_products():
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    col_map = {
        "id": [Product.product_id],
        "name": [Product.product_name],
        "ticker": [Product.ticker_symbol],
        "price": [Product.current_price],
        "sector": [Product.sector],
    }
    cols = col_map.get(sort, col_map["id"])  # default id
    order_by = [c.desc() if order == "desc" else c.asc() for c in cols]

    products = Product.query.order_by(*order_by).all()
    return render_template("products/list.html", products=products, sort=sort, order=order)


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        if form.ticker_symbol.data:
            exists = db.session.scalar(
                db.select(Product).where(Product.ticker_symbol == form.ticker_symbol.data)
            )
            if exists:
                flash("Ticker Symbol must be unique.", "danger")
                return render_template("products/create.html", form=form)

        product = Product(
            product_name=form.product_name.data,
            ticker_symbol=form.ticker_symbol.data or None,
            current_price=form.current_price.data if form.current_price.data is not None else None,
            sector=form.sector.data or None,
        )
        db.session.add(product)
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/create.html", form=form)


@bp.route("/<int:product_id>/delete", methods=["POST"])
@manager_required
def delete_product(product_id: int):
    product = Product.query.get(product_id)
    if product is None:
        raise NotFound()
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for("products.list_products"))


