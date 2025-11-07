from __future__ import annotations

from flask import Blueprint, render_template
from sqlalchemy import text

from .. import db

bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.get("/")
def index():
    return render_template("reports/index.html")


@bp.get("/kyc-contact-audit")
def kyc_contact_audit():
    # JOIN: Customer Name, Aadhar Number, Count of Phone Numbers
    # 3-Table Join with filtering on Risk Tolerance and COUNT()
    sql = text(
        """
        SELECT 
          CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
          d.aadhar_number AS aadhar_number,
          COUNT(ph.phone_id) AS phone_count
        FROM customers c
        JOIN customer_details d ON d.C_ID = c.C_ID
        LEFT JOIN customer_phones ph ON ph.C_ID = c.C_ID
        WHERE d.risk_tolerance IN ('low','medium','high')
        GROUP BY c.C_ID, d.aadhar_number
        ORDER BY phone_count DESC
        """
    )
    rows = db.session.execute(sql).mappings().all()
    return render_template("reports/kyc_contact_audit.html", rows=rows)


@bp.get("/aum-by-currency")
def aum_by_currency():
    # Aggregate: Currency, Total Invested Value (SUM), GROUP BY, HAVING
    # Assuming invested value approximated as SUM(quantity*price_per_unit) per currency
    sql = text(
        """
        SELECT 
          p.currency AS currency,
          SUM(t.quantity * t.price_per_unit) AS total_invested
        FROM portfolios p
        JOIN transactions t ON t.p_id = p.p_id
        GROUP BY p.currency
        HAVING SUM(t.quantity * t.price_per_unit) > 0
        ORDER BY total_invested DESC
        """
    )
    rows = db.session.execute(sql).mappings().all()
    return render_template("reports/aum_by_currency.html", rows=rows)


@bp.get("/tech-sector-employee-investors")
def tech_sector_employee_investors():
    # Nested/Subquery filtering employees involved with Portfolios owning Transactions in Tech sector
    sql = text(
        """
        SELECT DISTINCT e.E_name AS employee_name, e.job_title
        FROM employees e
        WHERE e.E_ID IN (
          SELECT p.E_ID
          FROM portfolios p
          JOIN transactions t ON t.P_ID = p.P_ID
          JOIN products pr ON pr.Product_ID = t.Product_ID
          WHERE pr.sector = 'Tech' AND p.E_ID IS NOT NULL
        )
        ORDER BY e.E_name ASC
        """
    )
    rows = db.session.execute(sql).mappings().all()
    return render_template("reports/tech_sector_employee_investors.html", rows=rows)


