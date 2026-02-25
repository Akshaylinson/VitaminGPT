import sqlite3
import json
from datetime import datetime
from pathlib import Path

DATABASE_PATH = Path("./data/vitamin_system.db")

def init_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            image_path TEXT,
            detected_disease TEXT,
            confidence_score REAL,
            vitamin_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    
    conn.commit()
    conn.close()

def add_patient(patient_id, name, address, phone):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO patients (id, name, address, phone) VALUES (?, ?, ?, ?)",
        (patient_id, name, address, phone)
    )
    conn.commit()
    conn.close()

def add_report(report_id, patient_id, image_path, detected_disease, confidence_score, vitamin_data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO reports (report_id, patient_id, image_path, detected_disease, 
           confidence_score, vitamin_data, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (report_id, patient_id, image_path, detected_disease, confidence_score, 
         json.dumps(vitamin_data), datetime.now())
    )
    conn.commit()
    conn.close()

def get_patient_reports(patient_id):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reports WHERE patient_id = ? ORDER BY created_at DESC",
        (patient_id,)
    )
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    for report in reports:
        report['vitamin_data'] = json.loads(report['vitamin_data'])
    
    return reports

def get_patient(patient_id):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return dict(patient) if patient else None
