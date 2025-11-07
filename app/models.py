from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import UniqueConstraint, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db


class Customer(db.Model):
    __tablename__ = "customers"

    c_id: Mapped[int] = mapped_column("C_ID", db.Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(db.Date, nullable=True)
    address: Mapped[str | None] = mapped_column(db.String(255), nullable=True)

    details: Mapped[Optional["CustomerDetails"]] = relationship(
        back_populates="customer", uselist=False, cascade="all, delete-orphan"
    )
    phones: Mapped[List["CustomerPhone"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    emails: Mapped[List["CustomerEmail"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    portfolios: Mapped[List["Portfolio"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer {self.c_id} {self.first_name} {self.last_name}>"


class CustomerDetails(db.Model):
    __tablename__ = "customer_details"

    c_id: Mapped[int] = mapped_column("C_ID", ForeignKey("customers.C_ID"), primary_key=True)
    ssn: Mapped[str | None] = mapped_column(db.String(20), nullable=True, unique=True)
    pan_number: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True)
    aadhar_number: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True)
    occupation: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    annual_income: Mapped[float | None] = mapped_column(db.Numeric(15, 2), nullable=True)
    risk_tolerance: Mapped[str | None] = mapped_column(
        db.Enum("low", "medium", "high", name="risk_tolerance_enum"), nullable=True
    )

    customer: Mapped[Customer] = relationship(back_populates="details")


class CustomerPhone(db.Model):
    __tablename__ = "customer_phones"

    phone_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    c_id: Mapped[int] = mapped_column("C_ID", ForeignKey("customers.C_ID"), nullable=False)
    phone_number: Mapped[str] = mapped_column(db.String(20), nullable=False)
    phone_type: Mapped[str | None] = mapped_column(
        db.Enum("mobile", "home", "work", name="phone_type_enum"), nullable=True
    )

    customer: Mapped[Customer] = relationship(back_populates="phones")


class CustomerEmail(db.Model):
    __tablename__ = "customer_emails"

    email_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    c_id: Mapped[int] = mapped_column("C_ID", ForeignKey("customers.C_ID"), nullable=False)
    email_address: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    email_type: Mapped[str | None] = mapped_column(
        db.Enum("personal", "work", "other", name="email_type_enum"), nullable=True
    )

    customer: Mapped[Customer] = relationship(back_populates="emails")


class Employee(db.Model):
    __tablename__ = "employees"

    e_id: Mapped[int] = mapped_column("E_ID", db.Integer, primary_key=True, autoincrement=True)
    employee_name: Mapped[str] = mapped_column("E_name", db.String(100), nullable=False)
    job_title: Mapped[str | None] = mapped_column(db.String(100), nullable=True)
    hire_date: Mapped[date | None] = mapped_column(db.Date, nullable=True)
    specialization: Mapped[str | None] = mapped_column(db.String(255), nullable=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.E_ID"), nullable=True)

    manager: Mapped[Optional["Employee"]] = relationship(remote_side=[e_id])
    portfolios: Mapped[List["Portfolio"]] = relationship(back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee {self.e_id} {self.employee_name}>"


class Product(db.Model):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column("Product_ID", db.Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column("Product_name", db.String(255), nullable=False)
    ticker_symbol: Mapped[str] = mapped_column(db.String(10), nullable=False, unique=True)
    current_price: Mapped[float | None] = mapped_column(db.Numeric(10, 2), nullable=True)
    sector: Mapped[str | None] = mapped_column(db.String(100), nullable=True)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"<Product {self.product_id} {self.product_name}>"


class Portfolio(db.Model):
    __tablename__ = "portfolios"

    p_id: Mapped[int] = mapped_column("P_ID", db.Integer, primary_key=True, autoincrement=True)
    portfolio_name: Mapped[str] = mapped_column("P_name", db.String(100), nullable=False)
    c_id: Mapped[int | None] = mapped_column("C_ID", ForeignKey("customers.C_ID"), nullable=True)
    e_id: Mapped[int | None] = mapped_column("E_ID", ForeignKey("employees.E_ID"), nullable=True)
    creation_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    risk_level: Mapped[str | None] = mapped_column(
        db.Enum("low", "medium", "high", name="portfolio_risk_enum"), nullable=True
    )
    currency: Mapped[str | None] = mapped_column(db.String(10), nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship(back_populates="portfolios")
    employee: Mapped[Optional["Employee"]] = relationship(back_populates="portfolios")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="portfolio")

    __table_args__ = (
        CheckConstraint(
            "(c_id IS NOT NULL) OR (e_id IS NOT NULL)",
            name="chk_portfolio_dual_ownership",
        ),
    )


class Transaction(db.Model):
    __tablename__ = "transactions"

    t_id: Mapped[int] = mapped_column("T_ID", db.Integer, primary_key=True, autoincrement=True)
    p_id: Mapped[int] = mapped_column("P_ID", ForeignKey("portfolios.P_ID"), nullable=False)
    product_id: Mapped[int] = mapped_column("Product_ID", ForeignKey("products.Product_ID"), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    commission_fee: Mapped[float | None] = mapped_column(db.Numeric(8, 2), nullable=True)

    portfolio: Mapped[Portfolio] = relationship(back_populates="transactions")
    product: Mapped[Product] = relationship(back_populates="transactions")


