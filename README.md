
# Insurance Management System

A Python-based insurance management system designed to simplify customer, insurance policy, installment tracking, and payment management for insurance offices.

The application provides a centralized workflow for registering insurance policies, automatically generating installment schedules, monitoring upcoming and overdue installments, recording payments, searching customer and installment information, and exporting installment data to Excel.

---

## 📌 About the Project

Managing insurance policies and installment payments can become difficult when customer information, policy details, payment schedules, and due dates are handled manually.

This project was developed to provide a practical solution for managing these processes in one application.

The system is built around four main sections:
1. Register New Insurance Policy
2. Alerts
3. Search by Date
4. Search Customer

Each section provides specific tools for managing insurance and installment information.

---

## ✨ Main Features

### 1. 📝 Register New Insurance Policy
This section guides the user through registering a new insurance policy.

**Customer Information:**
Before registering the policy, the customer's information is entered. The system supports searching for an existing customer using their National ID. If the National ID already exists in the database:
* First name is automatically retrieved
* Last name is automatically retrieved
* Phone number is automatically retrieved

The user can still modify the automatically populated information if necessary. This reduces repetitive data entry when an existing customer purchases another insurance policy.

**Insurance Policy Information:**
After entering the customer information, the user enters the insurance policy details. The system supports two payment types:
* Cash
* Installment

For a cash policy, installment-related fields are automatically hidden because they are not required.

For an installment-based policy, the user can specify:
* Down payment
* Number of installments
* Installment type
* Registration date

**📅 Persian Date Picker:**
The registration date is selected using a Persian calendar/date picker rather than requiring the user to manually enter a date. This reduces the possibility of invalid or incorrectly formatted date input.

**💰 Automatic Installment Calculation:**
For installment-based policies, installment amounts are calculated automatically based on:
* Total policy amount
* Down payment
* Number of installments

The system also handles rounding differences so that the total of all installments and the down payment exactly matches the policy's total amount.

### 2. 🔔 Alerts
The Alerts section helps the user monitor installments that require attention. It contains two tabs:

* **🔴 Overdue Installments:** Displays installments whose due dates have already passed and which have not yet been paid. Each installment includes a payment option so the user can record the payment directly from this section.
* **🟡 Urgent Installments:** Displays installments that are due Today, Tomorrow, or The day after tomorrow. Each installment also has a payment option. This allows the insurance office to quickly identify payments that require immediate attention.

**📊 Excel Export:**
The installment lists can be exported to an Excel file. This makes it possible to use the installment information for reporting, printing, sharing, or further processing.

### 3. 🔎 Search by Date
The user can select a specific date and retrieve all installments whose due date matches that date. The results include relevant information such as:
* Customer information
* Installment information
* Installment amount
* Due date
* Payment status
* Payment option

The user can mark an installment as paid directly from the search results. The results can also be exported to Excel.

### 4. 👤 Search Customer
The user can search for a customer using their National ID. After finding the customer, the system displays the customer's insurance policies along with their installment information. This allows the user to see the customer's insurance history and payment schedules in one place.

---

## 🧮 Installment Management

The installment calculation system is designed to handle the financial logic of installment-based insurance policies.

For example, if a policy has:
* **Total amount:** `100,000,000`
* **Down payment:** `20,000,000`
* **Remaining amount:** `80,000,000`
* **Number of installments:** `3`

The system automatically calculates:
* Installment 1: `26,666,666`
* Installment 2: `26,666,666`
* Installment 3: `26,666,668`

The remaining rounding amount is added to the final installment so that:
`Down payment + Sum(Installments) = Total policy amount`

This prevents rounding errors in financial calculations.

---

## 💳 Payment Management

Installments can be marked as paid directly from different parts of the application. Payment functionality is available from:
* Overdue installments
* Urgent installments
* Date-based search results

The system records the payment status and payment date. Once an installment is paid, it is no longer treated as an unpaid installment in the relevant views.

---

## 🗃️ Database

The application uses SQLite for local data storage and SQLAlchemy as the ORM. The database manages relationships between:

```text
Customer
   │
   └── Policy
          │
          └── Installment

```

This structure allows a customer to have multiple insurance policies, while each policy can have multiple installments. The local database file is excluded from version control through `.gitignore`.

---

## 🧪 Testing

The project uses `pytest` for automated testing. Tests cover important business logic and application behavior, including:

* `test_customer_policies_search.py` — Customer policy history search logic
* `test_database.py` — Database connection, engine initialization, and constraints
* `test_get_customer.py` & `test_save_customer.py` — Customer retrieval, lookup, and registration logic
* `test_helpers.py` — String normalization, digit conversion, and helper utilities
* `test_installment_calculator.py` — Installment amount calculation, division, and rounding logic
* `test_installment_report_servcie.py` — Installment reporting and status queries
* `test_jalali_date.py` — Jalali/Gregorian date conversion and formatting
* `test_payment.py` — Installment payment processing and status updates
* `test_policy_creation.py` — Policy creation workflows (cash vs. installment)
* `test_validators.py` — National ID and input validation rules

All current tests pass successfully.

Run the complete test suite with:

```bash
pytest

```

For more detailed output:

```bash
pytest -v

```

---

## 🛠️ Tech Stack

* **Python** — Main programming language
* **Streamlit** — Web application interface
* **SQLAlchemy** — ORM and database interaction
* **SQLite** — Local database
* **Pandas** — Data processing and Excel export
* **OpenPyXL** — Excel file generation
* **Jdatetime** — Jalali/Gregorian date handling
* **streamlit-nej-datepicker** — Persian date picker
* **streamlit-keyup** — Enhanced Streamlit input handling
* **num2fawords** — Persian number-to-words conversion
* **Pytest** — Automated testing

---

## 📁 Project Structure

```text
insurance-manager/
│
├── src/
│   ├── constant/       # Application constants and configuration flags
│   ├── database/       # SQLAlchemy models and connection setup
│   ├── services/       # Core business logic (Policy, Customer, Payment, Reports)
│   ├── ui/             # Streamlit user interface pages and layout
│   │   └── components/ # Reusable UI components (sidebar, picker, forms)
│   ├── utils/          # Utility functions (validators, date tools, helpers)
│   └── __init__.py
│
├── tests/              # Automated Pytest suite (unit & integration tests)
│
├── app.py              # Application entry point
├── config.py           # Project settings and configuration
├── requirements.txt    # Third-party dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation

```

---

## 🚀 Installation & Setup

1. **Clone the repository:**
```bash
git clone <YOUR-REPOSITORY-URL>
cd insurance-manager

```


2. **Create a virtual environment:**
* **Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```


* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```




3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Run the application:**
```bash
streamlit run app.py

```



The application will automatically open in your default browser.

---

## 🎯 Project Goals

This project was built as a practical software project around a real-world insurance management workflow. The main goals were to:

* Automate repetitive insurance-office tasks
* Reduce repetitive customer data entry
* Automate installment calculations
* Reduce financial calculation errors
* Provide quick access to upcoming and overdue payments
* Simplify payment tracking
* Provide searchable insurance and customer information
* Enable Excel-based reporting
* Apply software engineering practices such as modular design, validation, database modeling, and automated testing

---

## 🔮 Future Improvements

Potential future improvements include:

* SMS notifications for upcoming installments
* Automatic reminders for overdue payments
* User authentication and role management
* More advanced financial reports
* Dashboard and statistical views
* Automated database backups
* Cloud/production database support
* Production deployment
* More extensive integration and end-to-end testing

---

## 👩‍💻 Author

Developed by a Computer Engineering student as a personal project to solve a real-world insurance management problem while gaining hands-on experience in software development, database design, testing, and application architecture.



