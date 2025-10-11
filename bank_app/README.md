# 🏦 Bank Loan Management System

A full-stack web application that simulates a bank loan approval system. Users can apply for housing, auto, or personal loans, and the system calculates monthly payments, checks debt-to-income ratios, and stores approved/rejected applications in a CSV file.

Built with **Flask (Python)** for the backend and a **responsive vanilla HTML/CSS/JavaScript** frontend.

---

## ✨ Features

- **Three Loan Types** with fixed rates and term limits:
  - **Housing Loan**: 5.2% interest, up to 25 years
  - **Auto Loan**: 7.5% interest, up to 6 years
  - **Personal Loan**: 9.6% interest, up to 10 years
- **Real-time loan calculation** using the standard amortization formula
- **Debt-to-Income (DTI) Validation**: Ensures monthly payment ≤ 50% of user’s income
- **Smart User Guidance**:
  - If rejected, suggests increasing term (up to max) or reducing loan amount
- **Persistent Storage**: Finalized loans saved to `loan_records.csv`
- **Responsive Single-Page UI** with clear feedback and error handling

---

## 📁 Project Structure

```
bank-loan-system/
│
├── app.py                 # Flask backend with API endpoints
├── templates/
│   └── index.html         # Frontend UI (responsive single-page app)
└── loan_records.csv       # Auto-generated CSV file for loan records
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.6+
- `pip` package manager

### Installation
1. Clone or download this project.
2. Install Flask:
   ```bash
   pip install Flask
   ```
3. Navigate to the project directory.

### Running the Application
```bash
python app.py
```
Then open your browser and go to:  
👉 [http://localhost:5000](http://localhost:5000)

The first time you finalize a loan, `loan_records.csv` will be created automatically.

---

## 📝 Loan Calculation Logic

Monthly payment is calculated using the standard formula:

$$
M = P \cdot \frac{r(1 + r)^n}{(1 + r)^n - 1}
$$

Where:
- $ M $ = Monthly payment  
- $ P $ = Loan amount (principal)  
- $ r $ = Monthly interest rate (annual rate ÷ 12 ÷ 100)  
- $ n $ = Total number of payments (term in years × 12)

Total interest = $ (M \times n) - P $

Approval requires:  
**Monthly Payment ≤ 50% of Monthly Income**

---

## 📊 Sample CSV Output (`loan_records.csv`)

```csv
Loan Type,Loan Amount,Interest Rate,Term,Monthly Payment,Total Interest,Status
Housing Loan,200000,5.2%,20,1339.23,121415.2,Approved
Auto Loan,30000,7.5%,6,518.92,7358.24,Rejected
```

---

## 🛡️ Validation & Error Handling

The system validates:
- All numeric inputs are positive numbers
- Loan term does not exceed type-specific maximums
- Debt-to-income ratio compliance
- Proper loan type selection

Clear error messages guide users to correct inputs.

