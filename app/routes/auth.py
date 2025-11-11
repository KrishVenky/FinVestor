"""Authentication routes for login and logout."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .. import db
from ..auth import login_required
from ..forms import LoginForm, SignupForm
from ..models import User, Customer, Employee

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    # If already logged in, redirect to home
    if "user_id" in session:
        return redirect(url_for("products.list_products"))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.is_active:
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", form=form)
        
        # Verify password
        if not user.check_password(password):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", form=form)
        
        # Login successful - set session
        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role
        session["entity_type"] = user.get_entity_type()
        session["entity_id"] = user.get_entity_id()
        
        flash(f"Welcome back, {user.username}!", "success")
        
        # Redirect to requested page or home
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("products.list_products"))
    
    return render_template("auth/login.html", form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup with employee or customer ID."""
    # If already logged in, redirect to home
    if "user_id" in session:
        return redirect(url_for("products.list_products"))
    
    form = SignupForm()
    
    if form.validate_on_submit():
        entity_type = form.entity_type.data
        entity_id = form.entity_id.data
        username = form.username.data.strip()
        password = form.password.data
        password_confirm = form.password_confirm.data
        
        # Validate password confirmation
        if password != password_confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/signup.html", form=form)
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Please choose a different username.", "danger")
            return render_template("auth/signup.html", form=form)
        
        # Validate entity exists and determine role
        c_id = None
        e_id = None
        role = "regular"
        
        if entity_type == "customer":
            customer = db.session.get(Customer, entity_id)
            if customer is None:
                flash(f"Customer with ID {entity_id} not found. Please contact an administrator to create your customer record first.", "danger")
                return render_template("auth/signup.html", form=form)
            
            # Check if customer is already linked to a user
            existing_link = User.query.filter_by(c_id=entity_id).first()
            if existing_link:
                flash(f"Customer ID {entity_id} is already linked to an account. Please contact support if you need access.", "danger")
                return render_template("auth/signup.html", form=form)
            
            c_id = entity_id
            role = "regular"
        else:  # employee
            employee = db.session.get(Employee, entity_id)
            if employee is None:
                flash(f"Employee with ID {entity_id} not found. Please contact an administrator to create your employee record first.", "danger")
                return render_template("auth/signup.html", form=form)
            
            # Check if employee is already linked to a user
            existing_link = User.query.filter_by(e_id=entity_id).first()
            if existing_link:
                flash(f"Employee ID {entity_id} is already linked to an account. Please contact support if you need access.", "danger")
                return render_template("auth/signup.html", form=form)
            
            e_id = entity_id
            role = "employee"
        
        # Create user account
        user = User(
            username=username,
            role=role,
            c_id=c_id,
            e_id=e_id,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f"Account created successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/signup.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    username = session.get("username", "User")
    session.clear()
    flash(f"Goodbye, {username}. You have been logged out.", "info")
    return redirect(url_for("auth.login"))

