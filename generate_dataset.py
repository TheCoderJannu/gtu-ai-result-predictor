import json
import os
import numpy as np
import pandas as pd
from config import Config


def load_subject_catalog():
    """Load subject catalog from JSON file."""
    if not os.path.exists(Config.SUBJECTS_JSON_PATH):
        raise FileNotFoundError(f"Catalog file not found at {Config.SUBJECTS_JSON_PATH}")

    with open(Config.SUBJECTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_gtu_dataset(num_samples=7000, random_seed=42):
    """
    Generates realistic synthetic GTU student dataset with probabilistic correlations.
    
    Academic Correlations:
    - SPI (4.0 - 10.0) represents student baseline capability.
    - Attendance (35% - 100%) correlates with SPI + random variance.
    - Study Hours (4 - 35 hrs/wk) correlates with SPI and Attendance.
    - Active Backlogs (0 - 6) inversely correlates with SPI.
    - Mid1 (0 - 10) correlates with SPI and Attendance.
    - Mid2 (0 - 20) correlates with Mid1 and Study Hours.
    - Stage missingness (Before Mid-1 -> Mid1/Mid2 NaN; After Mid-1 -> Mid2 NaN).
    - Composite Score determines GTU Grade (AA, AB, BB, BC, CC, CD, DD, FF) and Pass status directly.
    """
    np.random.seed(random_seed)
    catalog = load_subject_catalog()

    # Flatten subject list
    subject_pool = []
    for dept, sems in catalog.items():
        for sem_str, sub_list in sems.items():
            sem_num = int(sem_str.replace("Semester", "").strip())
            for sub in sub_list:
                subject_pool.append({
                    "department": dept,
                    "semester": sem_num,
                    "subject": sub["subject_name"],
                    "difficulty": sub["difficulty"]
                })

    stages = ["Before Mid-1", "After Mid-1", "After Mid-2"]

    records = []

    for _ in range(num_samples):
        # Pick random subject metadata
        selected_sub = subject_pool[np.random.choice(len(subject_pool))]
        dept = selected_sub["department"]
        sem = selected_sub["semester"]
        sub_name = selected_sub["subject"]
        difficulty = selected_sub["difficulty"]
        stage = np.random.choice(stages, p=[0.30, 0.35, 0.35])

        # Baseline student potential: SPI between 4.0 and 10.0
        spi = round(float(np.clip(np.random.normal(loc=7.1, scale=1.3), 4.0, 10.0)), 2)

        # Attendance % correlated with SPI
        att_mean = 55.0 + (spi * 4.0)
        attendance = round(float(np.clip(np.random.normal(loc=att_mean, scale=7.0), 35.0, 100.0)), 1)

        # Study hours weekly correlated with SPI
        study_mean = 6.0 + (spi * 2.2)
        study_hours = round(float(np.clip(np.random.normal(loc=study_mean, scale=3.5), 4.0, 35.0)), 1)

        # Backlogs inversely correlated with SPI
        if spi >= 8.0:
            backlog_probs = [0.95, 0.04, 0.01, 0.0, 0.0, 0.0, 0.0]
        elif spi >= 6.5:
            backlog_probs = [0.80, 0.14, 0.04, 0.01, 0.01, 0.0, 0.0]
        elif spi >= 5.0:
            backlog_probs = [0.45, 0.30, 0.15, 0.06, 0.02, 0.01, 0.01]
        else:
            backlog_probs = [0.15, 0.25, 0.30, 0.15, 0.10, 0.03, 0.02]

        backlogs = int(np.random.choice([0, 1, 2, 3, 4, 5, 6], p=backlog_probs))

        # Difficulty Penalty
        diff_penalty = 0.0 if difficulty == "Easy" else (3.0 if difficulty == "Medium" else 6.0)

        # Simulated Internal Mid Marks
        mid1_mean = (spi * 0.85) + (attendance * 0.015) - (backlogs * 0.3) - (diff_penalty * 0.15)
        mid1_raw = round(float(np.clip(np.random.normal(loc=mid1_mean, scale=0.9), 0.0, 10.0)), 1)

        mid2_mean = (mid1_raw * 1.7) + (study_hours * 0.12) - (backlogs * 0.4) - (diff_penalty * 0.2)
        mid2_raw = round(float(np.clip(np.random.normal(loc=mid2_mean, scale=1.4), 0.0, 20.0)), 1)

        # Composite score calculation for direct GTU Grade labeling (0 to 100)
        composite = (
            (spi * 3.5) +                          # Max 35 pts from SPI
            (attendance * 0.15) +                  # Max 15 pts from Attendance
            (mid1_raw * 2.0) +                     # Max 20 pts from Mid1
            (mid2_raw * 1.0) +                     # Max 20 pts from Mid2
            (study_hours * 0.4) -                  # Max 14 pts from Study
            (backlogs * 4.5) -                     # Penalty for backlogs
            diff_penalty +                          # Difficulty penalty
            np.random.normal(loc=0, scale=1.5)     # Natural exam variance
        )

        composite = float(np.clip(composite, 15.0, 98.0))

        # Assign Direct GTU Grades
        if composite >= 84.0:
            grade = "AA"
            perf_cat = "Excellent"
        elif composite >= 74.0:
            grade = "AB"
            perf_cat = "Excellent"
        elif composite >= 64.0:
            grade = "BB"
            perf_cat = "Very Good"
        elif composite >= 54.0:
            grade = "BC"
            perf_cat = "Good"
        elif composite >= 45.0:
            grade = "CC"
            perf_cat = "Average"
        elif composite >= 40.0:
            grade = "CD"
            perf_cat = "Average"
        elif composite >= 35.0:
            grade = "DD"
            perf_cat = "At Risk"
        else:
            grade = "FF"
            perf_cat = "At Risk"

        is_pass = 1 if grade != "FF" else 0

        # Stage specific missing value handling
        if stage == "Before Mid-1":
            mid1_val = np.nan
            mid2_val = np.nan
        elif stage == "After Mid-1":
            mid1_val = mid1_raw
            mid2_val = np.nan
        else:  # After Mid-2
            mid1_val = mid1_raw
            mid2_val = mid2_raw

        records.append({
            "Department": dept,
            "Semester": sem,
            "Subject": sub_name,
            "Assessment Stage": stage,
            "Attendance": attendance,
            "SPI": spi,
            "Study Hours": study_hours,
            "Backlogs": backlogs,
            "Mid1": mid1_val,
            "Mid2": mid2_val,
            "Expected Grade": grade,
            "Pass": is_pass,
            "Performance Category": perf_cat
        })

    df = pd.DataFrame(records)
    
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    df.to_csv(Config.DATASET_PATH, index=False)
    print(f"[Dataset] Generated {len(df)} records successfully -> {Config.DATASET_PATH}")
    print("\nDataset Summary:")
    print(f"- Departments: {df['Department'].nunique()}")
    print(f"- Subjects: {df['Subject'].nunique()}")
    print(f"- Pass Rate: {(df['Pass'].mean() * 100):.1f}%")
    print(f"- Grade Distribution:\n{df['Expected Grade'].value_counts()}")

    return df


if __name__ == "__main__":
    generate_gtu_dataset(7000)
