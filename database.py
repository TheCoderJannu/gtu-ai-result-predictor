import json
import os
import sqlite3
from config import Config


def get_db_connection():
    """Establish connection to SQLite database with dictionary cursor row factory."""
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed subjects from JSON catalog if table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create subjects table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            internal_marks INTEGER NOT NULL,
            external_marks INTEGER NOT NULL,
            difficulty TEXT NOT NULL
        )
    """
    )

    # Create prediction_logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL,
            subject TEXT NOT NULL,
            assessment_stage TEXT NOT NULL,
            attendance_pct REAL NOT NULL,
            spi_last_sem REAL NOT NULL,
            weekly_study_hours REAL NOT NULL,
            active_backlogs INTEGER NOT NULL,
            mid1_marks REAL,
            mid2_marks REAL,
            predicted_pass_prob REAL NOT NULL,
            predicted_grade TEXT NOT NULL,
            performance_category TEXT NOT NULL,
            prediction_confidence REAL NOT NULL
        )
    """
    )

    conn.commit()

    # Seed subjects catalog if empty
    cursor.execute("SELECT COUNT(*) FROM subjects")
    count = cursor.fetchone()[0]

    if count == 0 and os.path.exists(Config.SUBJECTS_JSON_PATH):
        with open(Config.SUBJECTS_JSON_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)

        records = []
        for dept, sems in catalog.items():
            for sem_str, subject_list in sems.items():
                sem_num = int(sem_str.replace("Semester", "").strip())
                for sub in subject_list:
                    records.append(
                        (
                            dept,
                            sem_num,
                            sub["subject_code"],
                            sub["subject_name"],
                            sub["credits"],
                            sub["internal_marks"],
                            sub["external_marks"],
                            sub["difficulty"],
                        )
                    )

        cursor.executemany(
            """
            INSERT INTO subjects 
            (department, semester, subject_code, subject_name, credits, internal_marks, external_marks, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            records,
        )

        conn.commit()
        print(f"[DB] Initialized database and seeded {len(records)} subjects.")
    else:
        print(f"[DB] Database initialized. Found {count} subject records.")

    conn.close()


def get_all_departments():
    """Retrieve list of distinct GTU departments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT department FROM subjects ORDER BY department ASC"
    )
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return [row["department"] for row in rows]
    return Config.DEPARTMENTS


def get_all_semesters():
    """Retrieve list of available semester numbers (1 to 8)."""
    return list(range(1, 9))


def get_subjects_by_dept_and_sem(department, semester):
    """Retrieve subjects matching department and semester."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT subject_code, subject_name, credits, internal_marks, external_marks, difficulty 
        FROM subjects 
        WHERE department = ? AND semester = ?
        ORDER BY subject_code ASC
    """,
        (department, int(semester)),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_subject_by_code(subject_code):
    """Retrieve details for a subject by subject code."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT subject_code, subject_name, credits, internal_marks, external_marks, difficulty, department, semester
        FROM subjects
        WHERE subject_code = ?
    """,
        (subject_code,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_subject_by_name(department, semester, subject_name):
    """Retrieve details for a subject by name in department and semester."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT subject_code, subject_name, credits, internal_marks, external_marks, difficulty, department, semester
        FROM subjects
        WHERE department = ? AND semester = ? AND (subject_name = ? OR subject_code = ?)
    """,
        (department, int(semester), subject_name, subject_name),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_prediction_log(data):
    """Save a prediction result log to SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO prediction_logs (
            department, semester, subject, assessment_stage,
            attendance_pct, spi_last_sem, weekly_study_hours, active_backlogs,
            mid1_marks, mid2_marks, predicted_pass_prob, predicted_grade,
            performance_category, prediction_confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data["department"],
            int(data["semester"]),
            data["subject"],
            data["assessment_stage"],
            float(data["attendance_pct"]),
            float(data["spi_last_sem"]),
            float(data["weekly_study_hours"]),
            int(data["active_backlogs"]),
            data.get("mid1_marks"),
            data.get("mid2_marks"),
            float(data["predicted_pass_prob"]),
            data["predicted_grade"],
            data["performance_category"],
            float(data["prediction_confidence"]),
        ),
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def fetch_all_prediction_logs():
    """Retrieve all historical prediction logs ordered by creation date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, created_at, department, semester, subject, assessment_stage,
               attendance_pct, spi_last_sem, weekly_study_hours, active_backlogs,
               mid1_marks, mid2_marks, predicted_pass_prob, predicted_grade,
               performance_category, prediction_confidence
        FROM prediction_logs
        ORDER BY id DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_prediction_log(log_id):
    """Delete a prediction log entry by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prediction_logs WHERE id = ?", (int(log_id),))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


if __name__ == "__main__":
    init_db()
