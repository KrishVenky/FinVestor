from __future__ import annotations

from datetime import date
from typing import List, Tuple

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    RadioField,
    FieldList,
    FormField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Email


class CustomerForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
    address = TextAreaField("Address", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Create Customer")


class PhoneSubForm(FlaskForm):
    phone_number = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    phone_type = SelectField(
        "Phone Type",
        choices=[("mobile", "Mobile"), ("home", "Home"), ("work", "Work")],
        validators=[Optional()],
    )


class EmailSubForm(FlaskForm):
    email_address = StringField("Email Address", validators=[Optional(), Email(), Length(max=100)])
    email_type = SelectField(
        "Email Type",
        choices=[("personal", "Personal"), ("work", "Work"), ("other", "Other")],
        validators=[Optional()],
    )


class CustomerDetailsForm(FlaskForm):
    ssn = StringField("SSN", validators=[Optional(), Length(max=20)])
    pan_number = StringField("PAN Number", validators=[DataRequired(), Length(max=20)])
    aadhar_number = StringField("Aadhar Number", validators=[DataRequired(), Length(max=20)])
    occupation = StringField("Occupation", validators=[Optional(), Length(max=100)])
    annual_income = DecimalField("Annual Income", validators=[Optional(), NumberRange(min=0)])
    risk_tolerance = RadioField(
        "Risk Tolerance",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        validators=[Optional()],
    )
    phones = FieldList(FormField(PhoneSubForm), min_entries=1, max_entries=10)
    emails = FieldList(FormField(EmailSubForm), min_entries=1, max_entries=10)
    submit = SubmitField("Save KYC & Contacts")


class EmployeeForm(FlaskForm):
    employee_name = StringField("Employee Name", validators=[DataRequired(), Length(max=100)])
    job_title = StringField("Job Title", validators=[Optional(), Length(max=100)])
    hire_date = DateField("Hire Date", validators=[Optional()])
    specialization = StringField("Specialization", validators=[Optional(), Length(max=255)])
    manager_id = SelectField("Manager", coerce=int, validators=[Optional()])
    submit = SubmitField("Create Employee")


class ProductForm(FlaskForm):
    product_name = StringField("Product Name", validators=[DataRequired(), Length(max=255)])
    ticker_symbol = StringField("Ticker Symbol", validators=[DataRequired(), Length(max=10)])
    current_price = DecimalField("Current Price", validators=[Optional(), NumberRange(min=0)])
    sector = SelectField(
        "Sector",
        choices=[
            ("", "-- Select --"),
            ("Tech", "Tech"),
            ("Finance", "Finance"),
            ("Healthcare", "Healthcare"),
            ("Energy", "Energy"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Create Product")


class PortfolioForm(FlaskForm):
    portfolio_name = StringField("Portfolio Name", validators=[DataRequired(), Length(max=100)])
    c_id = SelectField("Customer Owner", coerce=int, validators=[Optional()])
    e_id = SelectField("Employee Owner", coerce=int, validators=[Optional()])
    creation_date = DateField("Creation Date", validators=[DataRequired()])
    risk_level = SelectField(
        "Risk Level",
        choices=[("", "-- Select --"), ("low", "Low"), ("medium", "Medium"), ("high", "High")],
        validators=[Optional()],
    )
    currency = SelectField(
        "Currency",
        choices=[
            ("", "-- Select --"),
            ("USD", "USD"),
            ("INR", "INR"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
            ("JPY", "JPY"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Create Portfolio")


class TransactionForm(FlaskForm):
    user = SelectField("User", coerce=str, validators=[DataRequired()])
    p_id = SelectField("Portfolio", coerce=int, validators=[DataRequired()])
    product_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    price_per_unit = DecimalField("Price per Unit", validators=[DataRequired(), NumberRange(min=0)])
    commission_rate = DecimalField(
        "Commission Rate",
        default=20,
        validators=[Optional()],
        render_kw={"readonly": True, "disabled": True},
    )
    submit = SubmitField("Submit Trade")


