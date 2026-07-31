/**
 * History Table & Log Manager with Sorting & Filtering
 * GTU Student Exam Readiness System
 */

document.addEventListener("DOMContentLoaded", function () {
    let historyLogs = [];

    const historyTbody = document.getElementById("historyTbody");
    const historyEmptyState = document.getElementById("historyEmptyState");
    const logCountBadge = document.getElementById("logCountBadge");

    const searchInput = document.getElementById("searchHistory");
    const filterStage = document.getElementById("filterStage");
    const filterCategory = document.getElementById("filterCategory");
    const sortHistory = document.getElementById("sortHistory");

    const btnRefresh = document.getElementById("btnRefreshHistory");

    // Modal elements
    const logModalEl = document.getElementById("logModal");
    const logModal = logModalEl ? new bootstrap.Modal(logModalEl) : null;
    const modalSubject = document.getElementById("modalSubject");
    const modalBody = document.getElementById("modalBody");

    function fetchHistory() {
        fetch("/api/history")
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    historyLogs = data.history;
                    applyFilters();
                }
            })
            .catch(err => console.error("Failed to load history logs:", err));
    }

    function renderTable(logs) {
        historyTbody.innerHTML = "";
        if (logCountBadge) {
            logCountBadge.textContent = `${logs.length} Logs`;
        }

        if (logs.length === 0) {
            historyEmptyState.classList.remove("d-none");
            document.getElementById("historyTable").classList.add("d-none");
            return;
        } else {
            historyEmptyState.classList.add("d-none");
            document.getElementById("historyTable").classList.remove("d-none");
        }

        logs.forEach(log => {
            const tr = document.createElement("tr");

            const dateStr = log.created_at ? log.created_at.split(" ")[0] : "Recent";

            let catBadge = "bg-secondary";
            if (log.performance_category === "Excellent") catBadge = "bg-success";
            else if (log.performance_category === "Very Good" || log.performance_category === "Good") catBadge = "bg-primary";
            else if (log.performance_category === "Average") catBadge = "bg-warning text-dark";
            else catBadge = "bg-danger";

            tr.innerHTML = `
                <td class="ps-3 text-muted small">${escapeHtml(dateStr)}</td>
                <td>
                    <div class="fw-semibold text-dark">${escapeHtml(log.department)}</div>
                    <div class="small text-muted">Semester ${log.semester}</div>
                </td>
                <td class="fw-semibold">${escapeHtml(log.subject)}</td>
                <td><span class="badge bg-light text-dark border">${escapeHtml(log.assessment_stage)}</span></td>
                <td class="fw-bold ${log.predicted_pass_prob >= 75 ? 'text-success' : 'text-danger'}">${log.predicted_pass_prob}%</td>
                <td><span class="badge grade-${escapeHtml(log.predicted_grade)}">${escapeHtml(log.predicted_grade)}</span></td>
                <td><span class="badge ${catBadge}">${escapeHtml(log.performance_category)}</span></td>
                <td class="pe-3 text-end">
                    <button class="btn btn-sm btn-outline-primary me-1 view-btn" data-id="${log.id}">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${log.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;

            historyTbody.appendChild(tr);
        });

        // Attach event listeners to view & delete buttons
        document.querySelectorAll(".view-btn").forEach(btn => {
            btn.addEventListener("click", function () {
                const id = parseInt(this.getAttribute("data-id"));
                openLogModal(id);
            });
        });

        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", function () {
                const id = parseInt(this.getAttribute("data-id"));
                deleteLog(id);
            });
        });
    }

    function applyFilters() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
        const stage = filterStage ? filterStage.value : "";
        const category = filterCategory ? filterCategory.value : "";
        const sortVal = sortHistory ? sortHistory.value : "newest";

        let filtered = historyLogs.filter(log => {
            const matchesQuery = (
                log.subject.toLowerCase().includes(query) ||
                log.department.toLowerCase().includes(query)
            );
            const matchesStage = stage === "" || log.assessment_stage === stage;
            const matchesCategory = category === "" || log.performance_category === category;

            return matchesQuery && matchesStage && matchesCategory;
        });

        // Sorting
        if (sortVal === "newest") {
            filtered.sort((a, b) => b.id - a.id);
        } else if (sortVal === "oldest") {
            filtered.sort((a, b) => a.id - b.id);
        } else if (sortVal === "pass_high") {
            filtered.sort((a, b) => b.predicted_pass_prob - a.predicted_pass_prob);
        } else if (sortVal === "pass_low") {
            filtered.sort((a, b) => a.predicted_pass_prob - b.predicted_pass_prob);
        }

        renderTable(filtered);
    }

    if (searchInput) searchInput.addEventListener("input", applyFilters);
    if (filterStage) filterStage.addEventListener("change", applyFilters);
    if (filterCategory) filterCategory.addEventListener("change", applyFilters);
    if (sortHistory) sortHistory.addEventListener("change", applyFilters);

    if (btnRefresh) {
        btnRefresh.addEventListener("click", fetchHistory);
    }

    function openLogModal(id) {
        const log = historyLogs.find(l => l.id === id);
        if (!log || !logModal) return;

        modalSubject.textContent = log.subject;
        modalBody.innerHTML = `
            <div class="row g-3 mb-3">
                <div class="col-6">
                    <div class="small text-muted">Department</div>
                    <div class="fw-semibold">${escapeHtml(log.department)}</div>
                </div>
                <div class="col-6">
                    <div class="small text-muted">Semester & Stage</div>
                    <div class="fw-semibold">Sem ${log.semester} (${escapeHtml(log.assessment_stage)})</div>
                </div>
                <div class="col-6">
                    <div class="small text-muted">Attendance</div>
                    <div class="fw-semibold">${log.attendance_pct}%</div>
                </div>
                <div class="col-6">
                    <div class="small text-muted">Last Sem SPI</div>
                    <div class="fw-semibold">${log.spi_last_sem}</div>
                </div>
                <div class="col-6">
                    <div class="small text-muted">Weekly Study Hours</div>
                    <div class="fw-semibold">${log.weekly_study_hours} hrs/wk</div>
                </div>
                <div class="col-6">
                    <div class="small text-muted">Active Backlogs</div>
                    <div class="fw-semibold">${log.active_backlogs}</div>
                </div>
            </div>
            <hr>
            <div class="p-3 bg-light rounded-3 text-center">
                <div class="small text-muted mb-1">PREDICTION RESULT</div>
                <div class="d-flex justify-content-center align-items-center gap-3">
                    <span class="display-6 fw-bold text-success">${log.predicted_pass_prob}%</span>
                    <span class="badge grade-${escapeHtml(log.predicted_grade)} fs-4">${escapeHtml(log.predicted_grade)}</span>
                </div>
                <div class="small fw-semibold mt-1">${escapeHtml(log.performance_category)} (${log.prediction_confidence}% Confidence)</div>
            </div>
        `;

        logModal.show();
    }

    function deleteLog(id) {
        if (!confirm("Are you sure you want to delete this prediction log?")) return;

        fetch(`/api/history/${id}`, { method: "DELETE" })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    historyLogs = historyLogs.filter(l => l.id !== id);
                    applyFilters();
                } else {
                    alert("Failed to delete log.");
                }
            })
            .catch(err => console.error("Error deleting log:", err));
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial Fetch
    fetchHistory();
});
