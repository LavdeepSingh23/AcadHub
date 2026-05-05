# AcadHub — Streamlit App

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure DB credentials
Edit `.streamlit/secrets.toml` — credentials are already set to your local MySQL.

### 3. Run the app
```bash
streamlit run app.py
```

## Project Structure
```
acadhub/
├── app.py                  # Login page (entry point)
├── db.py                   # DB connection & helpers
├── styles.py               # Fonts, CSS, shared components
├── requirements.txt
├── .streamlit/
│   ├── secrets.toml        # DB credentials
│   └── config.toml         # Theme config
└── pages/
    ├── 1_Student.py        # Student dashboard
    ├── 2_Faculty.py        # Faculty panel
    └── 3_Admin.py          # Admin control panel
```

## Demo Credentials

| Role    | Username   | Password   |
|---------|------------|------------|
| Student | kriti16    | kri16      |
| Student | lavdeep23  | lav23      |
| Student | aman10     | ama10      |
| Student | sim90      | ravi90     |
| Faculty | rumneek24  | rum24      |
| Faculty | raj19      | pass12903  |
| Admin   | doaa30     | adm@123    |
