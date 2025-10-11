from flask import Flask, render_template, request, jsonify
import csv
import os

app = Flask(__name__)

# Loan configuration
LOAN_CONFIG = {
    "Housing Loan": {"rate": 5.2, "max_term": 25},
    "Auto Loan": {"rate": 7.5, "max_term": 10},  # Note: PDF says 6, prompt says 6 — using 6
    "Auto Loan": {"rate": 7.5, "max_term": 6},
    "Personal Loan": {"rate": 9.6, "max_term": 10}
}

def calculate_monthly_payment(principal, annual_rate, term_years):
    if principal <= 0 or term_years <= 0:
        return 0
    r = (annual_rate / 100) / 12
    n = term_years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
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
        return jsonify({
            "success": False,
            "message": "All numerical inputs must be valid numbers."
        }), 400

    if loan_amount <= 0 or term_years <= 0 or monthly_income <= 0:
        return jsonify({
            "success": False,
            "message": "All inputs must be positive numbers."
        }), 400

    if loan_type not in LOAN_CONFIG:
        return jsonify({
            "success": False,
            "message": "Invalid loan type."
        }), 400

    config = LOAN_CONFIG[loan_type]
    if term_years > config["max_term"]:
        return jsonify({
            "success": False,
            "message": f"Term exceeds maximum of {config['max_term']} years for {loan_type}."
        }), 400

    annual_rate = config["rate"]
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, term_years)
    total_interest = monthly_payment * term_years * 12 - loan_amount
    debt_ratio = monthly_payment / monthly_income

    is_approved = debt_ratio <= 0.5

    message = "Approved!" if is_approved else (
        "Warning: Your monthly payment exceeds 50% of your income. "
        "Consider reducing the loan amount or increasing the term (if possible)."
    )

    return jsonify({
        "success": True,
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "is_approved": is_approved,
        "message": message,
        "max_term": config["max_term"],
        "current_term": term_years,
        "loan_amount": loan_amount
    })

@app.route('/api/finalize', methods=['POST'])
def finalize():
    data = request.json

    required_fields = [
        'loan_type', 'loan_amount', 'term_years', 'monthly_payment',
        'total_interest', 'is_approved'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

    status = "Approved" if data['is_approved'] else "Rejected"

    # Get interest rate
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