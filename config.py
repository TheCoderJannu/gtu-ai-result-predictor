import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gtu-ai-exam-readiness-secret-key-2026")
    
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

    DATABASE_PATH = os.path.join(DATA_DIR, "gtu_app.db")
    SUBJECTS_JSON_PATH = os.path.join(DATA_DIR, "gtu_subjects.json")
    DATASET_PATH = os.path.join(DATA_DIR, "gtu_dataset.csv")
    MODEL_PATH = os.path.join(MODELS_DIR, "gtu_grade_model.joblib")
    METADATA_PATH = os.path.join(MODELS_DIR, "model_metadata.json")

    DEPARTMENTS = [
        "Computer Engineering",
        "Information Technology",
        "Mechanical Engineering",
        "Civil Engineering",
        "Electrical Engineering",
        "Electronics & Communication"
    ]
