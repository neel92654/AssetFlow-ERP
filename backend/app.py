from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "assetflow.db"

app = Flask(__name__)
CORS(app)

VALID_MAINTENANCE_STATES = {
    "Pending",
    "Approved",
    "Tech Assigned",
    "In Progress",
    "Resolved",
}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                head TEXT NOT NULL,
                parent_node TEXT,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                purpose TEXT,
                requested_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(resource_id) REFERENCES resources(id)
            );

            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_no TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL
            );
            """
        )

        users_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        if users_count == 0:
            conn.executemany(
                "INSERT INTO users (name, email, role, password_hash) VALUES (?, ?, ?, ?)",
                [
                    (
                        "System Admin",
                        "admin@assetflow.com",
                        "Admin",
                        generate_password_hash("admin123"),
                    ),
                    (
                        "Asset Manager",
                        "manager@assetflow.com",
                        "Asset Manager",
                        generate_password_hash("manager123"),
                    ),
                ],
            )

        departments_count = conn.execute("SELECT COUNT(*) AS count FROM departments").fetchone()["count"]
        if departments_count == 0:
            conn.executemany(
                "INSERT INTO departments (name, head, parent_node, status) VALUES (?, ?, ?, ?)",
                [
                    ("Information Technology", "David Chen", "Executive Board", "Active"),
                    ("Facilities Management", "Maria Rodriguez", "Operations", "Active"),
                    ("Legacy Hardware Support", "Unassigned", "Information Technology", "Archived"),
                ],
            )

        resources_count = conn.execute("SELECT COUNT(*) AS count FROM resources").fetchone()["count"]
        if resources_count == 0:
            conn.executemany(
                "INSERT INTO resources (name, type) VALUES (?, ?)",
                [
                    ("Conf Room A", "Facilities"),
                    ("Conf Room B", "Facilities"),
                    ("Projector 01", "Equipment"),
                    ("Projector 02", "Equipment"),
                    ("Fleet Vehicle C", "Vehicles"),
                ],
            )

        maintenance_count = conn.execute("SELECT COUNT(*) AS count FROM maintenance_requests").fetchone()["count"]
        if maintenance_count == 0:
            conn.executemany(
                "INSERT INTO maintenance_requests (ticket_no, title, severity, status) VALUES (?, ?, ?, ?)",
                [
                    ("MNT-8902", "HVAC Unit B Failure", "Critical", "Pending"),
                    ("MNT-8895", "Forklift #4 Battery", "Medium", "Pending"),
                    ("MNT-8850", "Office Chair Repair", "Low", "Approved"),
                    ("MNT-8890", "Conveyor Belt Jam", "Medium", "Tech Assigned"),
                    ("MNT-8812", "Generator Maintenance", "Critical", "In Progress"),
                    ("MNT-8799", "Replace Lighting Ballast", "Low", "Resolved"),
                ],
            )


@app.get("/api/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@app.post("/api/auth/login")
def login() -> Any:
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    with get_db() as conn:
        user = conn.execute("SELECT id, name, email, role, password_hash FROM users WHERE email = ?", (email,)).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Invalid credentials."}), 401

    return jsonify(
        {
            "message": "Login successful.",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
        }
    )


@app.get("/api/organization/departments")
def list_departments() -> Any:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, head, parent_node, status FROM departments ORDER BY id"
        ).fetchall()

    return jsonify(
        [
            {
                "id": row["id"],
                "name": row["name"],
                "head": row["head"],
                "parentNode": row["parent_node"],
                "status": row["status"],
            }
            for row in rows
        ]
    )


@app.post("/api/organization/departments")
def create_department() -> Any:
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    head = str(payload.get("head", "Unassigned")).strip() or "Unassigned"
    parent_node = str(payload.get("parentNode", "Executive Board")).strip() or "Executive Board"
    status = str(payload.get("status", "Active")).strip() or "Active"

    if not name:
        return jsonify({"message": "Department name is required."}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO departments (name, head, parent_node, status) VALUES (?, ?, ?, ?)",
            (name, head, parent_node, status),
        )

    return jsonify(
        {
            "id": cursor.lastrowid,
            "name": name,
            "head": head,
            "parentNode": parent_node,
            "status": status,
        }
    ), 201


@app.get("/api/resources")
def list_resources() -> Any:
    with get_db() as conn:
        rows = conn.execute("SELECT id, name, type FROM resources ORDER BY type, name").fetchall()

    return jsonify([{"id": row["id"], "name": row["name"], "type": row["type"]} for row in rows])


def has_booking_conflict(resource_id: int, date: str, start_time: str, end_time: str) -> bool:
    with get_db() as conn:
        overlap = conn.execute(
            """
            SELECT id
            FROM bookings
            WHERE resource_id = ?
              AND date = ?
              AND start_time < ?
              AND end_time > ?
            LIMIT 1
            """,
            (resource_id, date, end_time, start_time),
        ).fetchone()

    return overlap is not None


@app.get("/api/bookings")
def list_bookings() -> Any:
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT b.id, b.resource_id, r.name AS resource_name, b.date, b.start_time, b.end_time, b.purpose, b.requested_by
            FROM bookings b
            JOIN resources r ON r.id = b.resource_id
            ORDER BY b.date DESC, b.start_time DESC
            """
        ).fetchall()

    return jsonify(
        [
            {
                "id": row["id"],
                "resourceId": row["resource_id"],
                "resourceName": row["resource_name"],
                "date": row["date"],
                "startTime": row["start_time"],
                "endTime": row["end_time"],
                "purpose": row["purpose"],
                "requestedBy": row["requested_by"],
            }
            for row in rows
        ]
    )


@app.post("/api/bookings")
def create_booking() -> Any:
    payload = request.get_json(silent=True) or {}

    try:
        resource_id = int(payload.get("resourceId"))
    except (TypeError, ValueError):
        return jsonify({"message": "A valid resource is required."}), 400

    date = str(payload.get("date", "")).strip()
    start_time = str(payload.get("startTime", "")).strip()
    end_time = str(payload.get("endTime", "")).strip()
    purpose = str(payload.get("purpose", "")).strip()
    requested_by = str(payload.get("requestedBy", "Employee")).strip() or "Employee"

    if not (date and start_time and end_time):
        return jsonify({"message": "Date, start time, and end time are required."}), 400

    if start_time >= end_time:
        return jsonify({"message": "End time must be after start time."}), 400

    if has_booking_conflict(resource_id, date, start_time, end_time):
        return jsonify({"message": "Selected slot overlaps an existing booking."}), 409

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO bookings (resource_id, date, start_time, end_time, purpose, requested_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (resource_id, date, start_time, end_time, purpose, requested_by, datetime.utcnow().isoformat()),
        )

    return jsonify({"id": cursor.lastrowid, "message": "Booking request submitted."}), 201


@app.get("/api/maintenance/requests")
def list_maintenance_requests() -> Any:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, ticket_no, title, severity, status FROM maintenance_requests ORDER BY id"
        ).fetchall()

    return jsonify(
        [
            {
                "id": row["id"],
                "ticketNo": row["ticket_no"],
                "title": row["title"],
                "severity": row["severity"],
                "status": row["status"],
            }
            for row in rows
        ]
    )


@app.patch("/api/maintenance/requests/<int:request_id>/status")
def update_maintenance_status(request_id: int) -> Any:
    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip()

    if status not in VALID_MAINTENANCE_STATES:
        return jsonify({"message": "Invalid maintenance state."}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE maintenance_requests SET status = ? WHERE id = ?",
            (status, request_id),
        )

    if cursor.rowcount == 0:
        return jsonify({"message": "Maintenance request not found."}), 404

    return jsonify({"message": "Maintenance request updated.", "id": request_id, "status": status})


@app.get("/api/reports/summary")
def report_summary() -> Any:
    with get_db() as conn:
        total_assets = conn.execute("SELECT COUNT(*) AS count FROM resources").fetchone()["count"]
        department_count = conn.execute("SELECT COUNT(*) AS count FROM departments WHERE status != 'Archived'").fetchone()[
            "count"
        ]
        active_maintenance = conn.execute(
            "SELECT COUNT(*) AS count FROM maintenance_requests WHERE status != 'Resolved'"
        ).fetchone()["count"]
        total_bookings = conn.execute("SELECT COUNT(*) AS count FROM bookings").fetchone()["count"]

    return jsonify(
        {
            "totalAssets": total_assets,
            "activeDepartments": department_count,
            "openMaintenance": active_maintenance,
            "totalBookings": total_bookings,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
