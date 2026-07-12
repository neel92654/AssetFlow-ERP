![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue)
![License](https://img.shields.io/badge/License-Hackathon-green)

# <img width="35" height="35" alt="image" src="https://github.com/user-attachments/assets/4f772494-271f-46cb-9436-0bc9f8d171b9" /> AssetFlow-ERP

> **Enterprise Asset & Resource Management System**

AssetFlow-ERP is a centralized, robust ERP solution that enables organizations to efficiently manage physical assets and shared resources through asset lifecycle tracking, resource booking, maintenance workflows, audit management, analytics, and role-based access control.

---

## Problem Statement

Organizations often rely on disjointed spreadsheets or legacy systems to manage their assets. This results in inefficient tracking, duplicate allocations, scheduling conflicts, delayed maintenance, and poor audit visibility.

**AssetFlow-ERP** provides a centralized, modern web platform that simplifies these operations, combining an intuitive UI with a scalable backend architecture.

---

## ✨ Key Features

- **Secure Authentication & RBAC**: Role-Based Access Control (Admin, Asset Manager, Department Head, Employee).
- **Organization Management**: Manage departments, sub-departments, and employee directories.
- **Asset Lifecycle Tracking**: End-to-end tracking from registration and allocation to maintenance and retirement.
- **Advanced Allocation & Transfer Workflow**: Dynamic workflows requiring approval for transferring actively assigned assets.
- **Shared Resource Booking**: Real-time booking system with conflict detection.
- **Maintenance Workflows**: Track repair requests, technician assignments, and issue resolutions.
- **Comprehensive Audits**: Audit cycle management to verify physical assets.
- **Activity Logs & Notifications**: Detailed audit trails and real-time alerts.

---

## 🛠 Tech Stack

### Frontend
- **HTML5 & CSS3**
- **JavaScript (ES6+)**
- **TailwindCSS** (via CDN for rapid, modern styling)
- **Google Material Symbols** for iconography

### Backend
- **Python 3.12+**
- **Flask** (RESTful API architecture)
- **Marshmallow** (Data serialization and validation)
- **Gunicorn** (WSGI HTTP Server)

### Database & Security
- **MySQL** (Relational Database)
- **SQLAlchemy** (ORM)
- **JWT Authentication** (Secure session management)
- **bcrypt** (Password Hashing)

---

## 📂 Project Structure

```text
AssetFlow-ERP/
│
├── frontend/                  # Static frontend files (HTML, JS, CSS)
│   ├── js/api.js              # Centralized API fetching and auth logic
│   ├── login.html             # Entry point
│   ├── dashboard.html         # Main overview
│   └── ...                    # Other feature modules
│
├── backend/                   # Python Flask Backend
│   ├── wsgi.py                # WSGI entry point
│   ├── app.py                 # Flask app factory
│   ├── database/              # SQLAlchemy Models
│   ├── auth/                  # Authentication & User Management
│   ├── assets/                # Asset logic & endpoints
│   ├── allocation/            # Allocation & Transfer logic
│   └── ...                    # Other backend modules
│
├── requirements.txt           # Python dependencies
└── README.md
```

---

## ▶️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/AssetFlow-ERP.git
cd AssetFlow-ERP
```

### 2. Database Setup

Ensure you have MySQL installed and running. Create the database:

```sql
CREATE DATABASE assetflow_db;
```

### 3. Backend Environment Setup

Navigate to the backend directory and set up a virtual environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r ../requirements.txt
```

Create a `.env` file in the `backend/` directory with the following variables:

```env
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=assetflow_db
JWT_SECRET_KEY=your_super_secret_key
```

### 4. Run the Backend Server

Start the application using Gunicorn (Recommended for production/mac/linux) or standard Python:

```bash
# Using Gunicorn (Mac/Linux)
gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app

# OR using standard Flask development server
python wsgi.py
```

### 5. Launch the Frontend

Since the frontend is built with vanilla web technologies, simply open `frontend/login.html` in your browser. Alternatively, you can serve it via a simple HTTP server to avoid CORS issues:

```bash
cd ../frontend
python3 -m http.server 8000
```
Then navigate to `http://localhost:8000/login.html` in your browser.

---

## 👥 User Roles

- **Admin**: Full access to all systems, settings, and override capabilities.
- **Asset Manager**: Can register assets, manage allocations, and initiate audits.
- **Department Head**: Can approve transfer requests and view department-specific metrics.
- **Employee**: Can view assigned assets, request maintenance, and book shared resources.

---

## 📄 License

Developed as part of a Hackathon project for educational and demonstration purposes.
