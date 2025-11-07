# Financial Investment Platform GUI (Flask)

A Zerodha-like portfolio management app built with Flask, SQLAlchemy, and MySQL.

## Prerequisites (Windows 11)
- Python 3.11+
- MySQL server running at 127.0.0.1:3306 (default DB `financial_platform_db`)
- (Optional) PowerShell 7 (recommended)

## Setup

```powershell
# From the project root
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env and set credentials
# (Create the file if it doesn't exist)
# Example contents:
# FLASK_SECRET_KEY=dev-secret-change-me
# DB_USER=your_user
# DB_PASSWORD=your_password
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_NAME=financial_platform_db
# FLASK_RUN_HOST=127.0.0.1
# FLASK_RUN_PORT=5000
# FLASK_DEBUG=1

# Run the app
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

## Configuration
Set the following environment variables in `.env` (defaults shown):

```
FLASK_SECRET_KEY=dev-secret-change-me
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=financial_platform_db
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
FLASK_DEBUG=1
```

## Database Objects Expected
- Stored Procedure: `Process_Trade(p_id, product_id, quantity, price_per_unit, commission_rate)`
- Function: `Calculate_Age(dob DATE)`
- Trigger: `before_employee_insert` (sets `specialization='General Support'` when NULL)

## Features Implemented
- Master screens: Customers, Employees, Products
- Dependent sub-forms: KYC & Risk Profile, Phones, Emails (add/remove rows)
- Business screens: Portfolios (dual ownership), Trade Execution (stored procedure call)
- Trade user selection (Client/Employee) sets commission automatically (Client 20%, Employee 10%)
- Product price auto-fills on selection; server also defaults from product if blank
- Client View shows total net worth and per-portfolio purchased products
- Clickable table headers with sorting (ID default ascending)
- Reports: KYC Contact Audit, Total AUM by Currency, Tech Sector Employee Investors

## Notes
- Uniqueness checks: Ticker Symbol, Aadhar, Email; safe upsert for emails (prevents duplicates)
- Manager dropdown stores `E_ID`
- Age is displayed by calling the DB function
- Trigger is implicitly exercised on Employee insert
- `.gitignore` included to ignore venvs, caches, logs, and `.env`

## Next Improvements
- Add authentication/roles
- Pagination and search across lists
- Client-side enhancements (searchable dropdowns, modals)

## Create DB objects (function/procedure/trigger)
Run this once after tables exist (PowerShell):

```powershell
mysql -h 127.0.0.1 -P 3306 -u $env:DB_USER -p $env:DB_NAME < .\sql\objects.sql
```

Or with literals:

```powershell
mysql -h 127.0.0.1 -P 3306 -u your_user -p financial_platform_db < .\sql\objects.sql
```

Or interactively:
```sql
-- inside mysql client, after selecting DB
SOURCE sql/objects.sql;
```

