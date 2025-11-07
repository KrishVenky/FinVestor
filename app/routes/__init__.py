from __future__ import annotations

from flask import Flask, redirect, url_for


def register_blueprints(app: Flask) -> None:
    from .customers import bp as customers_bp
    from .employees import bp as employees_bp
    from .products import bp as products_bp
    from .portfolios import bp as portfolios_bp
    from .transactions import bp as transactions_bp
    from .reports import bp as reports_bp

    app.register_blueprint(customers_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(portfolios_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(reports_bp)

    # Root route -> redirect to Clients
    app.add_url_rule(
        "/",
        "home",
        lambda: redirect(url_for("products.list_products")),
    )


