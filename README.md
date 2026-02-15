
# StaffCore - HR & Payroll SaaS

A modern, multi-tenant HR and Payroll management system built with Django and Tailwind CSS.

## Features

- **Multi-Tenancy**: Isolated workspaces for each company.
- **HR Management**: Employee profiles, digital personnel files, contracts.
- **Attendance**: Digital timeclock, overtime calculation, attendance tracking.
- **Payroll**: 
  - Automated salary calculation (Base + Overtime + Allowances - Deductions).
  - Progressive Tax Brackets (ISLR logic).
  - PDF Payslip Generation.
  - Payroll Dashboard with burn-rate charts.

## Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/samuelopez2010/Sas---Payroll.git
    cd Sas---Payroll
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Create Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

## Default Login

Check `create_demo_users.py` (if available) or create a new user via `/register/`.

## Contributing

1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit changes (`git commit -m 'Add amazing feature'`).
4.  Push to branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.
