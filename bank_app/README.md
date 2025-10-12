# 🏦 Bank Loan Management System

A full-stack web application that simulates a **bank loan approval system**.
Users can apply for housing, auto, or personal loans, and the system automatically calculates monthly payments, checks debt-to-income ratios, and stores finalized loan decisions in a CSV file.

Built with **Flask (Python)** for the backend and **responsive HTML/CSS/JavaScript** for the frontend.

---

## ✨ Key Features

* **Three Loan Types** with fixed interest rates and maximum terms:

  * 🏠 **Housing Loan** — 5.2% interest, up to 25 years
  * 🚗 **Auto Loan** — 7.5% interest, up to 6 years
  * 💳 **Personal Loan** — 9.6% interest, up to 10 years
* **Automatic Amortization Calculation** using the standard loan formula
* **Debt-to-Income (DTI) Validation:** Loan is approved only if monthly payment ≤ 50% of user’s income
* **Interactive Guidance:**

  * Suggests extending term (up to loan type limit)
  * Suggests reducing loan amount to meet approval criteria
* **Persistent Record-Keeping:** Finalized loans stored in `loan_records.csv`
* **Clean, Responsive UI** with real-time results, helpful error messages, and smart recommendations

---

## 📁 Project Structure

```
bank-loan-system/
│
├── app.py                 # Flask backend with API endpoints
├── templates/
│   └── index.html         # Responsive frontend UI
└── loan_records.csv       # Auto-generated after first finalized loan
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.6 or newer
* `pip` package manager

### Installation

1. Clone or download this repository.
2. Install Flask:

   ```bash
   pip install Flask
   ```
3. Navigate to the project directory.

### Run the Application

```bash
python app.py
```

Then open your browser at:
👉 [http://localhost:5000](http://localhost:5000)

The first finalized loan automatically creates `loan_records.csv`.

---

## 🧮 Loan Calculation Logic

The monthly payment ( M ) is computed using the standard amortization formula:

[
M = P \times \frac{r(1+r)^n}{(1+r)^n - 1}
]

Where:

* **P** = Principal (loan amount)
* **r** = Monthly interest rate = Annual Rate ÷ 12 ÷ 100
* **n** = Total payments = Term (in years) × 12

**Total Interest** = (M × n) − P

✅ **Approval Condition:** Monthly Payment ≤ 50% of Monthly Income

---

## 📊 Sample CSV Output

```csv
Loan Type,Loan Amount,Interest Rate,Term,Monthly Payment,Total Interest,Status
Housing Loan,200000,5.2%,20,1339.23,121415.20,Approved
Auto Loan,30000,7.5%,6,518.92,7358.24,Rejected
```

---

## 🛡️ Validation & Error Handling

The application validates and guides users to fix input errors:

* All numeric inputs must be **positive values**
* Term cannot exceed the **maximum for the loan type**
* Displays warnings when **debt ratio exceeds 50%**
* Offers **action buttons** to adjust loan term or amount
* Provides clear, friendly error messages for invalid inputs

---

## 👥 Team Contributions

| Member      | Role              | Responsibilities                                                                   |
| ----------- | ----------------- | ---------------------------------------------------------------------------------- |
| **Henry**   | Backend Developer | Implemented Flask backend, API routes, loan logic, CSV storage, and validation.    |
| **Esi**     | UI/UX Developer   | Designed and styled the responsive frontend using HTML & CSS for better usability. |
| **Gabriel** | Frontend Engineer | Implemented client-side calculations, JavaScript logic, and dynamic user feedback. |

---

## 🧩 Challenges & Solutions

| Challenge                                                  | Resolution                                                                   |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Data mismatch between frontend and backend JSON fields** | Standardized request keys to snake_case to match Flask expectations.         |
| **Rounding errors in floating-point calculations**         | Applied consistent rounding (`round(value, 2)`) before sending responses.    |
| **Ensuring smooth user interaction for rejected loans**    | Added dynamic UI suggestions (buttons to extend term or reduce loan amount). |
| **Maintaining CSV integrity**                              | Checked for file existence and wrote header row automatically.               |

---

## 🧪 Sample Test Cases

| # | Loan Type | Amount ($) | Term (yrs) | Income ($/mo) | Result      | Notes                              |
| - | --------- | ---------- | ---------- | ------------- | ----------- | ---------------------------------- |
| 1 | Housing   | 200000     | 20         | 8000          | ✅ Approved  | DTI ≈ 0.34                         |
| 2 | Auto      | 30000      | 5          | 2000          | ⚠️ Rejected | DTI ≈ 0.63 → suggests term = 6 yrs |
| 3 | Personal  | 15000      | 10         | 2500          | ✅ Approved  | DTI ≈ 0.28                         |
| 4 | Auto      | 25000      | 6          | 1800          | ⚠️ Rejected | Suggests reducing loan amount      |

---

## 🧾 Deliverables Summary

* ✅ `app.py` (Flask backend)
* ✅ `templates/index.html` (frontend UI)
* ✅ `loan_records.csv` (auto-generated on finalize)
* ✅ This README documentation

---

## 🏁 Conclusion

The **Bank Loan Management System** fulfills all Lab 4 requirements:

* Accurate amortization and DTI validation
* Clear guidance for users
* Robust error handling and CSV record storage

