# FinSight 💰📊

> ⚠️ **All Rights Reserved**
> This repository is for portfolio and showcase purposes only.
> Do not copy, reuse, or redistribute without explicit permission from the author.

**FinSight** is a full-stack personal finance and investment intelligence platform, built as part of the **Infosys Springboard Virtual Internship**. It combines expense tracking, budget monitoring, financial goal planning, and a simulated investment/trading portfolio into a single web app with a FastAPI backend and a React (Vite) frontend.

---

## 📌 Project Overview

FinSight is organized into two milestones, each broken into parts:

**Milestone 1 - Core Personal Finance**
| Part | Feature | Status |
|------|---------|--------|
| 1 | Authentication & Profile | ✅ Active |
| 2 | Expense, Accounts & Transactions | ✅ Active |
| 3 | Budget Monitoring | ✅ Active |
| 4 | Financial Dashboard | ✅ Active |
| Extra | Bank Statement Import (CSV/Excel) | ✅ Active |

**Milestone 2 - Investing & Goals**
| Part | Feature | Status |
|------|---------|--------|
| 1 | Investment Portfolio Core | ✅ Active |
| 2 | Market Data & Returns (Alpha Vantage) | ✅ Active |
| 3 | Financial Goal Planning | ✅ Active |
| 4 | Portfolio Analytics Dashboard | ✅ Active |
| Extra | Simulated Trading Wallet | ✅ Active |

---

## ✨ Key Features

- **Authentication** - registration with email verification, JWT login, forgot/reset password, profile management, password change
- **Accounts, Categories & Transactions** - full CRUD for financial accounts, custom categories, and transaction logging
- **Bank Statement Import** - upload a CSV/Excel statement, map columns to transaction fields, preview parsed rows (with duplicate & error detection), then commit confirmed rows as real transactions - a two-step preview/commit flow so nothing is saved without user confirmation
- **Budgets** - set and monitor category-wise budgets with CRUD support
- **Dashboard** - a consolidated summary view aggregating income, expenses, and account balances
- **Investment Portfolio** - track stocks, mutual funds, ETFs, and bonds with market-data-enriched views
- **Market Data & Returns** - live price enrichment and return calculations via an external market data service
- **Financial Goals** - create savings goals, fund them directly, auto-allocate savings, and cover shortfalls
- **Simulated Trading Wallet** - deposit virtual cash, buy/sell holdings, and view trade history - no real money moves
- **Portfolio Analytics** - dedicated analytics service for deeper portfolio insights

---

## 🛠️ Tech Stack

**Backend**
| Tool | Purpose |
|------|---------|
| FastAPI | Core web framework |
| SQLAlchemy + Alembic | ORM and database migrations |
| PostgreSQL (`psycopg2-binary`) | Database |
| passlib + bcrypt | Password hashing |
| python-jose / joserfc | JWT authentication |
| pydantic-settings | Configuration management |
| APScheduler | Scheduled/background tasks |
| httpx | Outbound HTTP (market data calls) |
| pandas + openpyxl | Parsing CSV/Excel bank statements for import |

**Frontend**
| Tool | Purpose |
|------|---------|
| React 18 | UI library |
| Vite 7 | Build tool & dev server |
| React Router | Client-side routing |
| Axios | API communication |
| Recharts | Charts & data visualization |
| Tailwind CSS | Styling |
| lucide-react | Icon set |

**DevOps**
| Tool | Purpose |
|------|---------|
| GitHub Actions | CI - backend lint/compile checks + frontend build checks |

---

## 📂 Project Structure

```
FinSight/
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/                 # 6 migrations: users, investments, price cache,
│                                  #   goals, trading wallet, savings pool
├── alembic.ini
│
├── backend/
│   ├── main.py                   # FastAPI app entrypoint & router registration
│   ├── config.py                 # App/DB/email settings (gitignored - contains secrets)
│   ├── database.py                # SQLAlchemy engine/session setup
│   ├── core/
│   │   ├── dependencies.py        # Shared FastAPI dependencies (e.g. get_current_user)
│   │   └── security.py            # Password hashing & token utilities
│   ├── models/                    # SQLAlchemy models: user, account, category,
│   │                               #   transaction, budget, investment, price_cache,
│   │                               #   goal, trade
│   ├── routers/                   # API route definitions
│   │   ├── auth.py                 # Register, login, verify email, password reset
│   │   ├── accounts.py              # Account CRUD
│   │   ├── categories.py            # Category CRUD
│   │   ├── transactions.py          # Transaction CRUD + statement import (preview/commit)
│   │   ├── budgets.py               # Budget CRUD
│   │   ├── dashboard.py             # Aggregated dashboard summary
│   │   ├── investments.py           # Investment CRUD + market data views
│   │   ├── goals.py                 # Goal CRUD, funding, savings allocation
│   │   └── trading.py               # Simulated wallet: deposit, buy, sell, history
│   ├── schemas/                   # Pydantic request/response schemas
│   │   └── import_transactions.py  # ColumnMapping, ParsedImportRow, preview/commit schemas
│   ├── services/                  # Business logic layer (one service per domain)
│   │   └── import_service.py       # Parses uploaded statements, matches categories,
│   │                                #   flags likely duplicates, commits confirmed rows
│   ├── scripts/
│   │   └── generate_finvu_keys.py  # Key generation utility (Finvu integration)
│   ├── secrets/                    # Finvu keys (gitignored)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios API clients, one per domain
│   │   │   └── importApi.js         # Calls /transactions/import/preview & /commit
│   │   ├── components/
│   │   │   ├── common/              # Button, Card, Input, ProtectedRoute
│   │   │   ├── dashboard/           # Chart & summary strip components
│   │   │   └── layout/              # AppShell, Sidebar
│   │   ├── context/
│   │   │   └── AuthContext.jsx      # Auth state provider
│   │   ├── pages/                   # Login, Register, Dashboard, Accounts,
│   │   │                            #   Transactions (incl. import UI), Budgets, Goals,
│   │   │                            #   Investments, PortfolioDashboard, Profile,
│   │   │                            #   Forgot/Reset Password, VerifyEmail
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
└── .github/workflows/ci.yml       # CI: backend lint/compile + frontend build
```

---

## 🚀 How to Run

### Backend

1. Clone the repository:
   ```bash
   git clone https://github.com/jvnsuman/FinSight.git
   cd FinSight
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Create your own `backend/config.py` (not included in this repo) with your database URL, JWT secret, and email/SMTP settings.

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the API server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Create a `.env` file (see `.env.example`) pointing to your backend API URL.

3. Start the dev server:
   ```bash
   npm run dev
   ```

---

## 📥 Importing Bank Statements

1. Go to the **Transactions** page and choose **Import**
2. Upload a CSV/Excel bank statement and map its columns (date, description, amount, or separate debit/credit columns) to FinSight's transaction fields
3. Review the **preview** - parsed rows are shown with any parse errors or likely duplicates flagged, and category is suggested via a simple substring match against your existing categories
4. Edit any rows if needed, then **commit** - only at this point are transactions actually created in your ledger

---

## 🔐 Security Notes

- Passwords are hashed with **bcrypt** via `passlib`
- Authentication uses **JWT** tokens (`python-jose` / `joserfc`)
- Sensitive files (`backend/config.py`, `.env`, `backend/secrets/`) are excluded from version control via `.gitignore`

---

## 🏫 Internship

This project was developed as part of the **Infosys Springboard Virtual Internship** - a self-paced virtual internship program by Infosys.

---

## 👤 Author

**Jivan Suman**
GitHub: [@jvnsuman](https://github.com/jvnsuman)

---

© 2026 Jivan Suman. All Rights Reserved.
