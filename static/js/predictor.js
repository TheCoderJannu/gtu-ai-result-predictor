/**
 * Predictor Async Submission, Animations & Report Exporter
 * GTU Student Exam Readiness System
 */

document.addEventListener("DOMContentLoaded", function () {
    const btnPredict = document.getElementById("btnPredict");
    const btnText = document.getElementById("btnText");
    const btnSpinner = document.getElementById("btnSpinner");

    const resultPlaceholder = document.getElementById("resultPlaceholder");
    const resultCard = document.getElementById("resultCard");

    const resStageBadge = document.getElementById("resultStageBadge");
    const resPassProb = document.getElementById("resPassProb");
    const gaugeArc = document.getElementById("gaugeArc");
    const resGradeBadge = document.getElementById("resGradeBadge");
    const resCategory = document.getElementById("resCategory");
    const resConfidence = document.getElementById("resConfidence");

    const resFactorsContainer = document.getElementById("resFactorsContainer");
    const resStrengthsList = document.getElementById("resStrengthsList");
    const resWeaknessesList = document.getElementById("resWeaknessesList");
    const resRecommendationsList = document.getElementById("resRecommendationsList");

    const btnPrint = document.getElementById("btnPrintReport");
    const btnPdf = document.getElementById("btnDownloadPdf");

    // Print & PDF Export Event Listeners
    if (btnPrint) {
        btnPrint.addEventListener("click", function () {
            window.print();
        });
    }

    if (btnPdf) {
        btnPdf.addEventListener("click", function () {
            const reportEl = document.getElementById("pdfReportContent");
            const opt = {
                margin:       0.5,
                filename:     `GTU_Readiness_Report.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2 },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(reportEl).save();
        });
    }

    btnPredict.addEventListener("click", function () {
        if (btnPredict.disabled) return;

        // Collect Values
        const dept = document.getElementById("selectedDepartment").value;
        const sem = document.getElementById("selectedSemester").value;
        const subject = document.getElementById("subjectSelect").value;
        const stage = document.getElementById("selectedStage").value;

        const attendance = document.getElementById("inputAttendance").value;
        const spi = document.getElementById("inputSpi").value;
        const studyHours = document.getElementById("inputStudyHours").value;
        const backlogs = document.getElementById("inputBacklogs").value;

        const mid1 = document.getElementById("inputMid1").value;
        const mid2 = document.getElementById("inputMid2").value;

        // Basic Client Validation
        if (!dept) {
            alert("Please select a Department in Step 1.");
            return;
        }
        if (!sem) {
            alert("Please select a Semester in Step 2.");
            return;
        }
        if (!subject) {
            alert("Please select a Subject in Step 3.");
            return;
        }
        if (!attendance || !spi || !studyHours || backlogs === "") {
            alert("Please fill in all mandatory numerical input fields.");
            return;
        }
        if ((stage === "After Mid-1" || stage === "After Mid-2") && !mid1) {
            alert("Please enter Mid-1 marks.");
            return;
        }
        if (stage === "After Mid-2" && !mid2) {
            alert("Please enter Mid-2 marks.");
            return;
        }

        const payload = {
            department: dept,
            semester: parseInt(sem),
            subject: subject,
            assessment_stage: stage,
            attendance: parseFloat(attendance),
            spi: parseFloat(spi),
            study_hours: parseFloat(studyHours),
            backlogs: parseInt(backlogs),
            mid1_marks: mid1 ? parseFloat(mid1) : null,
            mid2_marks: mid2 ? parseFloat(mid2) : null
        };

        // Set Loading State (Prevents Duplicate Submissions)
        btnPredict.disabled = true;
        btnText.classList.add("d-none");
        btnSpinner.classList.remove("d-none");
        btnSpinner.classList.add("d-flex");

        // Send POST to /api/predict
        fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            btnPredict.disabled = false;
            btnText.classList.remove("d-none");
            btnSpinner.classList.add("d-none");
            btnSpinner.classList.remove("d-flex");

            if (data.status === "success") {
                renderDashboard(data, stage);
            } else {
                alert("Prediction Error: " + (data.message || "Unknown error"));
            }
        })
        .catch(err => {
            btnPredict.disabled = false;
            btnText.classList.remove("d-none");
            btnSpinner.classList.add("d-none");
            btnSpinner.classList.remove("d-flex");
            console.error("API Call Error:", err);
            alert("Failed to connect to backend prediction service.");
        });
    });

    function renderDashboard(data, stage) {
        const pred = data.prediction;
        const analysis = data.analysis;
        const recommendations = data.recommendations;

        // Update Stage Badge
        resStageBadge.textContent = stage;

        // Update Pass Probability & Animated Counter
        const passProb = pred.pass_probability;
        animateCounter(resPassProb, 0, passProb, 800, "%");

        // Circumference for r=65 is ~408.4
        const maxOffset = 408.4;
        const offset = maxOffset - (maxOffset * (passProb / 100.0));
        gaugeArc.style.strokeDashoffset = offset;

        // Gauge Stroke Color based on Pass Probability
        if (passProb >= 75) {
            gaugeArc.style.stroke = "#22C55E";
        } else if (passProb >= 50) {
            gaugeArc.style.stroke = "#F59E0B";
        } else {
            gaugeArc.style.stroke = "#EF4444";
        }

        // Expected Grade
        const grade = pred.expected_grade;
        resGradeBadge.textContent = grade;
        resGradeBadge.className = `grade-badge grade-${grade} mb-2`;

        // Category & Confidence
        resCategory.textContent = pred.performance_category;
        resConfidence.textContent = `Confidence: ${pred.confidence_score}%`;

        // Factors (Positive / Negative Impact)
        resFactorsContainer.innerHTML = "";
        if (pred.feature_contributions && pred.feature_contributions.length > 0) {
            pred.feature_contributions.forEach(f => {
                const pill = document.createElement("span");
                if (f.impact === "Positive") {
                    pill.className = "impact-pill-pos";
                    pill.innerHTML = `<i class="fa-solid fa-circle-plus me-1"></i> ${escapeHtml(f.factor)}: ${escapeHtml(f.value)}`;
                } else {
                    pill.className = "impact-pill-neg";
                    pill.innerHTML = `<i class="fa-solid fa-circle-minus me-1"></i> ${escapeHtml(f.factor)}: ${escapeHtml(f.value)}`;
                }
                resFactorsContainer.appendChild(pill);
            });
        }

        // Strengths
        resStrengthsList.innerHTML = "";
        analysis.strengths.forEach(s => {
            const li = document.createElement("li");
            li.textContent = s;
            resStrengthsList.appendChild(li);
        });

        // Weaknesses
        resWeaknessesList.innerHTML = "";
        analysis.weaknesses.forEach(w => {
            const li = document.createElement("li");
            li.textContent = w;
            resWeaknessesList.appendChild(li);
        });

        // Recommendations
        resRecommendationsList.innerHTML = "";
        recommendations.forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            resRecommendationsList.appendChild(li);
        });

        // Show Dashboard, Hide Placeholder
        resultPlaceholder.classList.add("d-none");
        resultCard.classList.remove("d-none");
        resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function animateCounter(elem, start, end, duration, suffix = "") {
        const range = end - start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / (range || 1)));
        let current = start;
        
        const timer = setInterval(() => {
            current += (range / 20);
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            elem.textContent = `${Math.round(current)}${suffix}`;
        }, 40);
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
