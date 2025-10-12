from flask import Flask, render_template, request, jsonify
import csv
import os
import math

app = Flask(__name__)

# Loan configuration (one "Auto Loan" entry, max 6 years)
LOAN_CONFIG = {
    "Housing Loan": {"rate": 5.2, "max_term": 25},
    "Auto Loan": {"rate": 7.5, "max_term": 6},
    "Personal Loan": {"rate": 9.6, "max_term": 10}
}

def calculate_monthly_payment(principal, annual_rate, term_years):
    """Amortized payment formula per assignment."""
    if principal <= 0 or term_years <= 0:
        return 0.0
    r = (annual_rate / 100.0) / 12.0
    n = int(term_years) * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

def max_affordable_loan(annual_rate, term_years, target_payment):
    """Solve principal from payment formula: P = M * ((1+r)^n - 1) / (r*(1+r)^n)."""
    r = (annual_rate / 100.0) / 12.0
    n = int(term_years) * 12
    if r == 0:
        return target_payment * n
    top = (1 + r) ** n - 1
    bottom = r * (1 + r) ** n
    return target_payment * (top / bottom)

def min_term_for_payment(principal, annual_rate, max_monthly_payment, max_term_cap):
    """
    Find the smallest integer term (years) where monthly payment <= max_monthly_payment,
    bounded by loan-type max term. Return None if not possible.
    """
    r = (annual_rate / 100.0) / 12.0
    # If r == 0, term = ceil(P / M / 12)
    if r == 0:
        n = math.ceil(principal / max_monthly_payment)  # months
        years = math.ceil(n / 12)
        return years if years <= max_term_cap else None

    # Binary search on term in months for minimal n s.t. payment <= cap
    lo, hi = 1, max_term_cap * 12
    feasible_n = None
    while lo <= hi:
        mid = (lo + hi) // 2  # months
        # payment at mid months
        M = principal * r * (1 + r) ** mid / ((1 + r) ** mid - 1)
        if M <= max_monthly_payment:
            feasible_n = mid
            hi = mid - 1
        else:
            lo = mid + 1

    if feasible_n is None:
        return None
    return math.ceil(feasible_n / 12)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json or {}
    # Expect snake_case keys from client
    loan_type = data.get('loan_type')
    loan_amount = data.get('loan_amount')
    term_years = data.get('term_years')
    monthly_income = data.get('monthly_income')

    # Input validation
    try:
        loan_amount = float(loan_amount)
        term_years = int(term_years)
        monthly_income = float(monthly_income)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "All numerical inputs must be valid numbers."}), 400

    if loan_amount <= 0 or term_years <= 0 or monthly_income <= 0:
        return jsonify({"success": False, "message": "All inputs must be positive numbers."}), 400

    if loan_type not in LOAN_CONFIG:
        return jsonify({"success": False, "message": "Invalid loan type."}), 400

    config = LOAN_CONFIG[loan_type]
    if term_years > config["max_term"]:
        return jsonify({"success": False, "message": f"Term exceeds maximum of {config['max_term']} years for {loan_type}."}), 400

    annual_rate = config["rate"]
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, term_years)
    total_interest = monthly_payment * term_years * 12 - loan_amount
    debt_ratio = monthly_payment / monthly_income  # <= 0.5 is required by brief

    is_approved = debt_ratio <= 0.5
    message = "Approved!" if is_approved else (
        "Warning: Your monthly payment exceeds 50% of your income. "
        "Consider increasing the term (if allowed) or reducing the loan amount."
    )

    # Guidance when not approved
    min_term_for_ok = None
    max_loan_for_current_term = None
    if not is_approved:
        # The max affordable payment under the 50% ratio:
        max_allowed_payment = 0.5 * monthly_income

        # 1) If user can extend term (within max), compute the minimum term to meet cap
        min_term_for_ok = min_term_for_payment(loan_amount, annual_rate, max_allowed_payment, config["max_term"])

        # 2) For current term, compute a max affordable principal for guidance
        max_loan_for_current_term = max_affordable_loan(annual_rate, term_years, max_allowed_payment)

    return jsonify({
        "success": True,
        "loan_type": loan_type,
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "is_approved": is_approved,
        "message": message,
        "debt_ratio": round(debt_ratio, 4),  # e.g., 0.42
        "max_term": config["max_term"],
        "current_term": term_years,
        "loan_amount": round(loan_amount, 2),
        "min_term_for_approval": min_term_for_ok,  # may be None
        "max_affordable_loan_for_current_term": round(max_loan_for_current_term, 2) if max_loan_for_current_term else None,
        "rate": annual_rate
    })

@app.route('/api/finalize', methods=['POST'])
def finalize():
    data = request.json or {}

    required_fields = [
        'loan_type', 'loan_amount', 'term_years', 'monthly_payment',
        'total_interest', 'is_approved'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

    status = "Approved" if data['is_approved'] else "Rejected"
    rate = LOAN_CONFIG.get(data['loan_type'], {}).get('rate', 0)

    file_exists = os.path.isfile('loan_records.csv')
    with open('loan_records.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Loan Type", "Loan Amount", "Interest Rate", "Term",
                "Monthly Payment", "Total Interest", "Status"
            ])
        writer.writerow([
            data['loan_type'],
            data['loan_amount'],
            f"{rate}%",
            data['term_years'],
            data['monthly_payment'],
            data['total_interest'],
            status
        ])

    return jsonify({"success": True, "message": "Loan record saved successfully."})

if __name__ == '__main__':
    app.run(debug=True)
