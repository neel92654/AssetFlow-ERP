![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue)
![License](https://img.shields.io/badge/License-Hackathon-green)

# <img width="35" height="35" alt="image" src="https://github.com/user-attachments/assets/4f772494-271f-46cb-9436-0bc9f8d171b9" /> AssetFlow-ERP

> **Enterprise Asset & Resource Management System**

AssetFlow-ERP is a centralized ERP solution that enables organizations to efficiently manage physical assets and shared resources through asset lifecycle tracking, resource booking, maintenance workflows, audit management, analytics, and role-based access control.

---

## Problem Statement

Organizations often rely on spreadsheets or disconnected systems to manage assets, resulting in inefficient tracking, duplicate allocations, scheduling conflicts, delayed maintenance, and poor audit visibility.

AssetFlow-ERP provides a centralized platform that simplifies these operations through an intuitive and scalable ERP system.

---

## ✨ Key Features

- Secure Authentication & Role-Based Access
- Department & Employee Management
- Asset Registration & Lifecycle Tracking
- Asset Allocation & Transfer Workflow
- Shared Resource Booking with Conflict Detection
- Maintenance Approval Workflow
- Audit Cycle Management
- Reports & Analytics Dashboard
- Activity Logs & Notifications

---

## 🛠 Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask (or FastAPI if you're using it)

### Database
- MySQL

### Authentication
- JWT Authentication
- Password Hashing (bcrypt)

---

## 📂 Project Structure

```text
AssetFlow-ERP/
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── organisationsetup.html
│   ├── Assetregistration.html
│   ├── Assetallocation.html
│   ├── resourcebooking.html
│   ├── Maintenancemanagement.html
│   ├── Assetaudit.html
│   ├── Reportandanalysis.html
│   └── Activitylogs.html
│
├── backend/
│   ├── app.py
│   ├── assetflow.db (auto-created)
│   ├── requirements.txt
│   └── README.md
├── database/
├── assets/
└── README.md
```

---

## 📸 Application Modules

- Login
- Dashboard
- Organization Setup
- Asset Registration
- Asset Allocation & Transfer
- Resource Booking
- Maintenance Management
- Asset Audit
- Reports & Analytics
- Activity Logs & Notifications

---

## 👥 User Roles

- **Admin**
- **Asset Manager**
- **Department Head**
- **Employee**

Each role has secure, role-based permissions for accessing different modules.

---

## ▶️ Getting Started

Clone the repository:

```bash
git clone https://github.com/<your-username>/AssetFlow-ERP.git
```

Navigate to the project:

```bash
cd AssetFlow-ERP
```

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Run the backend:

```bash
python app.py
```

Open `frontend/login.html` in your browser (or serve the frontend with your preferred local server).

---

## 📄 License

Developed as part of a Hackathon project for educational and demonstration purposes.

