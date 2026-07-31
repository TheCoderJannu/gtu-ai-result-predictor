import os
from flask import Flask, jsonify, render_template, request
from config import Config
from database import (
    delete_prediction_log,
    fetch_all_prediction_logs,
    init_db,
    save_prediction_log,
)
from utils.predictor import PredictorEngine
from utils.recommendation import RecommendationEngine
from utils.subject_service import SubjectService

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

# Ensure data and model directories exist
os.makedirs(Config.DATA_DIR, exist_ok=True)
os.makedirs(Config.MODELS_DIR, exist_ok=True)

# Initialize database schema and subject catalog on app startup
with app.app_context():
    init_db()


# -----------------------------------------------------------------------------
# WEB TEMPLATE PAGE ROUTES
# -----------------------------------------------------------------------------


@app.route("/", methods=["GET"])
def home():
    """Home landing page route."""
    return render_template("index.html")


@app.route("/predict", methods=["GET"])
def predict_page():
    """Prediction dashboard & 3-Step stepper route."""
    return render_template("predict.html")


@app.route("/history", methods=["GET"])
def history_page():
    """Prediction history logs viewer route."""
    return render_template("history.html")


@app.route("/about", methods=["GET"])
def about_page():
    """About project architecture & GTU documentation route."""
    return render_template("about.html")


# -----------------------------------------------------------------------------
# REST API ENDPOINTS
# -----------------------------------------------------------------------------


@app.route("/api/status", methods=["GET"])
def api_status():
    """Application status and API info endpoint."""
    return (
        jsonify(
            {
                "status": "online",
                "system": "AI-Based GTU Student Exam Readiness System",
                "version": "1.0.0",
                "phase": 4,
                "endpoints": [
                    "GET /api/departments",
                    "GET /api/semesters",
                    "GET /api/subjects?department={dept}&semester={sem}",
                    "GET /api/subject/{subject_code}",
                    "POST /api/predict",
                    "GET /api/history",
                    "DELETE /api/history/{id}",
                ],
            }
        ),
        200,
    )


@app.route("/api/departments", methods=["GET"])
def get_departments():
    """Retrieve all available GTU departments."""
    departments = SubjectService.list_departments()
    return jsonify({"status": "success", "departments": departments}), 200


@app.route("/api/semesters", methods=["GET"])
def get_semesters():
    """Retrieve supported GTU semesters (1 to 8)."""
    semesters = SubjectService.list_semesters()
    return jsonify({"status": "success", "semesters": semesters}), 200


@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    """
    Retrieve subjects filtered by department and semester.
    Query Params: ?department=Computer Engineering&semester=6
    """
    department = request.args.get("department", "").strip()
    semester_raw = request.args.get("semester", "").strip()

    if not department or not semester_raw:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Both 'department' and 'semester' parameters are required.",
                }
            ),
            400,
        )

    try:
        semester = int(semester_raw)
        if semester < 1 or semester > 8:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Semester must be between 1 and 8.",
                    }
                ),
                400,
            )
    except ValueError:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Semester must be a valid integer.",
                }
            ),
            400,
        )

    subjects = SubjectService.get_subjects(department, semester)
    return (
        jsonify(
            {
                "status": "success",
                "department": department,
                "semester": semester,
                "count": len(subjects),
                "subjects": subjects,
            }
        ),
        200,
    )


@app.route("/api/subject/<subject_code>", methods=["GET"])
def get_subject_by_code(subject_code):
    """Retrieve complete details for a single subject by its GTU code."""
    subject_info = SubjectService.get_subject_info_by_code(subject_code)
    if not subject_info:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Subject with code '{subject_code}' not found.",
                }
            ),
            404,
        )

    return jsonify({"status": "success", "subject": subject_info}), 200


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Predict GTU Student Exam Readiness, Pass Probability, Grade, and AI Analysis.
    JSON Payload Validation -> PredictorEngine -> RecommendationEngine -> SQLite Log.
    """
    if not request.is_json:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request payload must be valid JSON.",
                }
            ),
            400,
        )

    data = request.get_json()

    # Required Fields Validation
    required_fields = [
        "department",
        "semester",
        "subject",
        "assessment_stage",
        "attendance",
        "spi",
        "study_hours",
        "backlogs",
    ]

    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Missing required field: '{field}'",
                    }
                ),
                400,
            )

    department = str(data["department"]).strip()
    subject = str(data["subject"]).strip()
    stage = str(data["assessment_stage"]).strip()

    # Validate Semester
    try:
        semester = int(data["semester"])
        if semester < 1 or semester > 8:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Semester must be between 1 and 8.",
                    }
                ),
                400,
            )
    except ValueError:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Semester must be a valid integer.",
                }
            ),
            400,
        )

    # Validate Assessment Stage
    valid_stages = ["Before Mid-1", "After Mid-1", "After Mid-2"]
    if stage not in valid_stages:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Assessment stage must be one of: {valid_stages}",
                }
            ),
            400,
        )

    # Validate Numerical Ranges
    try:
        attendance = float(data["attendance"])
        spi = float(data["spi"])
        study_hours = float(data["study_hours"])
        backlogs = int(data["backlogs"])

        if not (0.0 <= attendance <= 100.0):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Attendance must be between 0.0 and 100.0%",
                    }
                ),
                400,
            )

        if not (0.0 <= spi <= 10.0):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "SPI must be between 0.0 and 10.0",
                    }
                ),
                400,
            )

        if not (0.0 <= study_hours <= 100.0):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Weekly study hours must be between 0.0 and 100.0",
                    }
                ),
                400,
            )

        if backlogs < 0 or backlogs > 30:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Active backlogs must be a non-negative integer.",
                    }
                ),
                400,
            )

    except ValueError:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid numeric format for attendance, spi, study_hours, or backlogs.",
                }
            ),
            400,
        )

    # Validate Mid Marks according to Assessment Stage
    mid1_marks = data.get("mid1_marks")
    mid2_marks = data.get("mid2_marks")

    if stage in ["After Mid-1", "After Mid-2"]:
        if mid1_marks is None or str(mid1_marks).strip() == "":
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Mid-1 marks (Out of 10) are required for stage '{stage}'.",
                    }
                ),
                400,
            )
        try:
            mid1_val = float(mid1_marks)
            if not (0.0 <= mid1_val <= 10.0):
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Mid-1 marks must be between 0.0 and 10.0.",
                        }
                    ),
                    400,
                )
            mid1_marks = mid1_val
        except ValueError:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Mid-1 marks must be a valid number.",
                    }
                ),
                400,
            )
    else:
        mid1_marks = None

    if stage == "After Mid-2":
        if mid2_marks is None or str(mid2_marks).strip() == "":
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Mid-2 marks (Out of 20) are required for stage 'After Mid-2'.",
                    }
                ),
                400,
            )
        try:
            mid2_val = float(mid2_marks)
            if not (0.0 <= mid2_val <= 20.0):
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Mid-2 marks must be between 0.0 and 20.0.",
                        }
                    ),
                    400,
                )
            mid2_marks = mid2_val
        except ValueError:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Mid-2 marks must be a valid number.",
                    }
                ),
                400,
            )
    else:
        mid2_marks = None

    # Retrieve Subject Information Card Details
    subject_info = SubjectService.get_subject_info(department, semester, subject)

    # Format payload for inference engine
    predictor_payload = {
        "department": department,
        "semester": semester,
        "subject": subject,
        "assessment_stage": stage,
        "attendance_pct": attendance,
        "spi_last_sem": spi,
        "weekly_study_hours": study_hours,
        "active_backlogs": backlogs,
        "mid1_marks": mid1_marks,
        "mid2_marks": mid2_marks,
    }

    try:
        # Run Machine Learning Prediction
        prediction_result = PredictorEngine.predict(predictor_payload)

        # Generate Strengths, Weaknesses, and Subject Topic Recommendations
        analysis = RecommendationEngine.analyze_strengths_and_weaknesses(
            predictor_payload
        )
        recommendations = RecommendationEngine.get_subject_recommendations(subject)

        # Save Prediction to SQLite Database
        log_payload = {
            "department": department,
            "semester": semester,
            "subject": subject,
            "assessment_stage": stage,
            "attendance_pct": attendance,
            "spi_last_sem": spi,
            "weekly_study_hours": study_hours,
            "active_backlogs": backlogs,
            "mid1_marks": mid1_marks,
            "mid2_marks": mid2_marks,
            "predicted_pass_prob": prediction_result["pass_probability"],
            "predicted_grade": prediction_result["predicted_grade"],
            "performance_category": prediction_result["performance_category"],
            "prediction_confidence": prediction_result["confidence_score"],
        }
        log_id = save_prediction_log(log_payload)

        return (
            jsonify(
                {
                    "status": "success",
                    "prediction_id": log_id,
                    "subject_info": subject_info,
                    "prediction": {
                        "pass_probability": prediction_result["pass_probability"],
                        "expected_grade": prediction_result["predicted_grade"],
                        "performance_category": prediction_result["performance_category"],
                        "confidence_score": prediction_result["confidence_score"],
                        "feature_contributions": prediction_result["feature_contributions"],
                    },
                    "analysis": analysis,
                    "recommendations": recommendations,
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Prediction pipeline failure: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/history", methods=["GET"])
def get_history():
    """Retrieve prediction logs history."""
    try:
        logs = fetch_all_prediction_logs()
        return jsonify({"status": "success", "count": len(logs), "history": logs}), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to fetch history logs: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/history/<int:log_id>", methods=["DELETE"])
def delete_history_item(log_id):
    """Delete a single prediction history log by ID."""
    try:
        success = delete_prediction_log(log_id)
        if not success:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Prediction log ID {log_id} not found.",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Prediction log ID {log_id} deleted successfully.",
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to delete history log: {str(e)}",
                }
            ),
            500,
        )


@app.errorhandler(404)
def not_found(error):
    # Check if API request or Web Browser request
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "API endpoint not found."}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Internal server error."}), 500
    return render_template("404.html"), 500


if __name__ == "__main__":
    print("[Flask] Starting GTU AI Backend & Web Platform...")
    app.run(debug=True, port=5000)
