# FlexLite (ERP-lite)

**FlexLite** is a lightweight, UI-focused ERP system designed for small to medium-sized teams. It streamlines core internal processes including Leave Management, Expense Reporting, and Certificate Issuance, backed by a robust **Approval Engine**.

## 🚀 Features

### 1. 🏖️ Leave Management (연차 관리)
- **Request**: Create leave requests (Annual, Half-day, Sick leave) with date range and reason.
- **Balance**: View remaining/used leave days (Dashboard).
- **Approval**: Manager approval required for finalization.

### 2. 💳 Expense Management (지출 결의)
- **Receipts**: Upload usage details and attach receipt images.
- **Reporting**: Bundle multiple receipts into a single **Expense Report** (지출결의서).
- **Workflow**: Submit reports for manager approval.

### 3. 📄 Certificate Issuance (증명서 발급)
- **Types**: Employment (재직), Career (경력), Income (소득) certificates.
- **Process**: Request -> Approval -> Download (PDF/Print).

### 4. 🖨️ Quote Management (견적서 관리)
- **Drafting**: Create quotes with line items (Quantity, Unit Price, Amount).
- **Process**: Draft -> Submit -> Approval -> Print/PDF.

### 5. ✅ Approval Engine (결재 시스템)
- **Inbox**: Centralized inbox for managers to view pending requests.
- **Review**: Approve or Reject with comments.
- **Source of Truth**: Critical state changes (e.g., Leave balance deduction) occur only upon final approval.

### 6. 📊 Export (엑셀 다운로드)
- **Automation**: Automatically generates Excel files (`.xlsx`) from approved documents.
- **Signatures**: Injects verification metadata/signatures into the output file.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, **Flask** (Blueprints)
- **Database**: **MariaDB** (Production) / SQLite (Dev), **SQLAlchemy** ORM
- **Frontend**: Server-side Rendering (**Jinja2**)
- **Styling**: **TailwindCSS** (CDN) for modern, responsive UI
- **Interaction**: **HTMX** (for dynamic partial updates)
- **Export**: `openpyxl`

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Environment Configuration
Check `.env` file for configuration:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev_key
DATABASE_URL=sqlite:///flexlite.db
UPLOAD_DIR=uploads
```

### 4. Initialize Database (Seed)
Run the seed script to create tables and default accounts:
```bash
python seed_flexlite.py
```

### 5. Run Server
```bash
python run.py
```
Server will start at `http://127.0.0.1:5000`

---

## 🔑 Test Accounts

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Employee** | `employee@flexlite.com` | `password` | Request Leave/Expense/Cert |
| **Manager** | `manager@flexlite.com` | `password` | Approve Requests, View Team |
| **Admin** | `admin@flexlite.com` | `password` | System Settings, Fallback Approval |

---

## 📂 Project Structure

```
c:\workspace\LeaveFlow\
├── app/
│   ├── models/          # Database Models (User, Leave, Approval...)
│   ├── routes/          # Blueprint Controllers (Auth, Main, Leave...)
│   ├── services/        # Business Logic (ApprovalService, ExportService)
│   ├── templates/       # Jinja2 HTML Templates (Tailwind styled)
│   └── static/          # Static assets (CSS/JS/Images)
├── uploads/             # User uploaded files
├── requirements.txt     # Python dependencies
├── run.py               # Application Entrypoint
├── seed_flexlite.py     # Database Seeder
└── .env                 # Environment Variables
```

---

## 🎨 UI/UX Philosophy
- **Lightweight**: Minimal JS bundle, leveraging Server-Side Rendering.
- **Flex Style**: Round corners, soft shadows, plenty of whitespace (Inter/Pretendard font).
- **Feedback**: Clear success/error messages via Flash messages.
