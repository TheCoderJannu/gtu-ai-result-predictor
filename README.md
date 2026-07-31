# AI-Based GTU Student Exam Readiness & Performance Prediction System

An AI-powered educational analytics web application designed specifically for Gujarat Technological University (GTU) students, faculty, and academic advisors. The system predicts exam readiness, pass probability (%), official GTU grades (`AA`, `AB`, `BB`, `BC`, `CC`, `CD`, `DD`, `FF`), performance risk categories, and provides domain-tailored revision topic guidance.

Designed after modern light-themed SaaS platforms (**Stripe, Linear, Vercel, Clerk, Notion**).

---

## 🌟 Key Features

- **Exhaustive GTU Syllabus Catalog**: 100% complete GTU curriculum covering **6 Engineering Departments** (*CE, IT, ME, CL, EE, EC*) across **Semesters 1 to 8** (190 core subjects with Subject Code, Credits, Internal 30 Marks, External 70 Marks, Difficulty index).
- **Progressive 3-Step Selection Stepper**: Interactive unlocking flow (Step 1: Department Grid $\rightarrow$ Step 2: Semester Pills $\rightarrow$ Step 3: Searchable Subject Dropdown).
- **Subject Information Card**: Auto-displays subject code, credits, internal evaluation marks, external theory marks, and difficulty level (*Easy / Medium / Hard*).
- **Stage-Aware Evaluation**: Supports 3 evaluation stages:
  1. *Before Mid-1* (Attendance %, SPI, Study Hours, Backlogs)
  2. *After Mid-1* (+ Mid-1 Marks out of 10)
  3. *After Mid-2* (+ Mid-2 Marks out of 20)
- **Direct GTU Grade ML Classifier**: Multi-class classification model trained on 7,000 synthetic GTU student records predicting official GTU grades (`AA` to `FF`) directly.
- **Explainable AI Analysis**: Highlights top positive and negative contributing factors for every prediction.
- **Subject-Specific Recommendations Engine**: Provides tailored GTU revision topic advice mapped per subject (e.g. Operating Systems, Computer Networks, Web Technology, Data Structures).
- **Prediction History & Log Store**: Full prediction history logger in SQLite with search, filtering, and deletion options.
- **PDF Report Export & Printing**: Instant 1-click print and PDF export of readiness reports.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask REST APIs, SQLite Database
- **Machine Learning**: Scikit-Learn (`HistGradientBoostingClassifier`, `RandomForestClassifier`), Pandas, NumPy, Joblib
- **Frontend**: HTML5, Vanilla CSS (Custom Light SaaS Theme), Bootstrap 5, Font Awesome 6, Vanilla JS, html2pdf.js

---

## 📁 Directory Structure

```text
c:/Users/compu/Desktop/intenship project 2.0/
├── app.py                      # Flask Main Application & REST Controller
├── config.py                   # App Configuration, GTU Constants & File Paths
├── generate_dataset.py         # Synthetic GTU Dataset Generator (7,000 records)
├── train_model.py              # ML Pipeline Builder & Direct Grade Classifier Trainer
├── database.py                 # SQLite Schema Setup, Subject Catalog & History Logs
├── requirements.txt            # Python dependencies
├── README.md                   # Complete System Documentation
│
├── data/
│   ├── gtu_subjects.json       # Complete GTU Master Catalog (6 Depts x 8 Sems)
│   ├── gtu_dataset.csv         # Synthetic GTU Student Dataset
│   └── gtu_app.db              # SQLite Database File
│
├── models/
│   ├── gtu_grade_model.joblib  # Serialized Scikit-Learn Model Pipeline
│   └── model_metadata.json     # Feature names, metrics & evaluation stats
│
├── utils/
│   ├── __init__.py
│   ├── subject_service.py      # GTU subject catalog service layer
│   ├── predictor.py            # Model inference engine & feature impact analysis
│   └── recommendation.py       # Subject-specific recommendation & strength/weakness engine
│
├── static/
│   ├── css/
│   │   └── main.css            # Custom Light SaaS Theme (Stripe/Linear aesthetic)
│   └── js/
│       ├── dynamic_form.js     # 3-Step Stepper & Searchable Dropdown JS
│       ├── predictor.js        # Prediction API submission, animations & PDF export
│       └── history.js          # Prediction history filtering, sorting & management
│
└── templates/
    ├── base.html               # SaaS base navigation, header & footer
    ├── index.html              # SaaS Landing Page (Hero, Features, Stats, Workflow)
    ├── predict.html            # 3-Step Stepper & Dynamic Result Dashboard
    ├── history.html            # Prediction History & Analytical Log Table
    ├── about.html              # Technical Documentation & GTU Grading Architecture
    └── 404.html                # Custom SaaS 404 Error Page
```

---

## 🚀 Installation & Execution Guide

### 1. Prerequisites
Ensure **Python 3.9+** is installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Subject Database & Generate Dataset (Optional - Pre-generated)
```bash
python generate_dataset.py
```

### 4. Train & Evaluate Machine Learning Pipeline
```bash
python train_model.py
```

### 5. Launch Application
```bash
python app.py
```

Access the application in your browser at: `http://127.0.0.1:5000`

---

## 🎯 Verification & System Status

- **Phase 1: Foundation & Data Architecture** — Completed & Verified.
- **Phase 2: Machine Learning Pipeline** — Completed & Verified (HistGradientBoosting ~69.86% multi-class accuracy).
- **Phase 3: Flask REST APIs & Backend Engine** — Completed & Verified.
- **Phase 4: SaaS Frontend UI & Dynamic Stepper Dashboard** — Completed & Verified.
- **Phase 5: System Integration, PDF Export & Final Polish** — Completed & Verified.
