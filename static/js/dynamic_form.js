/**
 * Dynamic Stepper & Form Control Handler
 * GTU Student Exam Readiness System
 */

document.addEventListener("DOMContentLoaded", function () {
    let currentDept = "";
    let currentSem = "";
    let subjectCatalog = [];

    // Elements
    const deptCards = document.querySelectorAll(".dept-card");
    const semPills = document.querySelectorAll(".sem-pill");
    const step2Container = document.getElementById("step2Container");
    const step3Container = document.getElementById("step3Container");
    
    const step1Ind = document.getElementById("stepIndicator1");
    const step2Ind = document.getElementById("stepIndicator2");
    const step3Ind = document.getElementById("stepIndicator3");

    const selectedDeptInput = document.getElementById("selectedDepartment");
    const selectedSemInput = document.getElementById("selectedSemester");
    
    const subjectSearchInput = document.getElementById("subjectSearchInput");
    const subjectSelect = document.getElementById("subjectSelect");
    const subjectInfoCard = document.getElementById("subjectInfoCard");

    const infoCode = document.getElementById("infoCode");
    const infoName = document.getElementById("infoName");
    const infoCredits = document.getElementById("infoCredits");
    const infoInternal = document.getElementById("infoInternal");
    const infoExternal = document.getElementById("infoExternal");
    const infoDifficulty = document.getElementById("infoDifficulty");

    const stageOptions = document.querySelectorAll("#stageSegmentedControl .segmented-option");
    const selectedStageInput = document.getElementById("selectedStage");

    const mid1Container = document.getElementById("mid1Container");
    const mid2Container = document.getElementById("mid2Container");
    const inputMid1 = document.getElementById("inputMid1");
    const inputMid2 = document.getElementById("inputMid2");

    // -------------------------------------------------------------------------
    // STEP 1: Department Card Selection
    // -------------------------------------------------------------------------
    deptCards.forEach(card => {
        card.addEventListener("click", function () {
            deptCards.forEach(c => c.classList.remove("selected"));
            this.classList.add("selected");

            currentDept = this.getAttribute("data-dept");
            selectedDeptInput.value = currentDept;

            step1Ind.classList.add("completed");
            step2Ind.classList.add("active");

            // Unlock Step 2
            step2Container.style.pointerEvents = "auto";
            step2Container.classList.remove("opacity-50");

            // Reset Step 3 if dept changed
            resetStep3();

            if (currentSem) {
                fetchSubjects(currentDept, currentSem);
            }
        });
    });

    // -------------------------------------------------------------------------
    // STEP 2: Semester Pill Selection
    // -------------------------------------------------------------------------
    semPills.forEach(pill => {
        pill.addEventListener("click", function () {
            semPills.forEach(p => p.classList.remove("selected"));
            this.classList.add("selected");

            currentSem = this.getAttribute("data-sem");
            selectedSemInput.value = currentSem;

            step2Ind.classList.add("completed");
            step3Ind.classList.add("active");

            // Unlock Step 3
            step3Container.style.pointerEvents = "auto";
            step3Container.classList.remove("opacity-50");

            if (currentDept) {
                fetchSubjects(currentDept, currentSem);
            }
        });
    });

    // -------------------------------------------------------------------------
    // STEP 3: Async Subject Fetch & Population
    // -------------------------------------------------------------------------
    function fetchSubjects(dept, sem) {
        subjectSearchInput.disabled = true;
        subjectSearchInput.placeholder = "Loading GTU subjects...";
        subjectSelect.style.display = "none";
        subjectInfoCard.classList.add("d-none");

        fetch(`/api/subjects?department=${encodeURIComponent(dept)}&semester=${encodeURIComponent(sem)}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === "success" && data.subjects.length > 0) {
                    subjectCatalog = data.subjects;
                    renderSubjectOptions(subjectCatalog);

                    subjectSearchInput.disabled = false;
                    subjectSearchInput.placeholder = "Search subject by name or code...";
                    subjectSelect.style.display = "block";
                } else {
                    subjectSelect.innerHTML = `<option value="">No subjects found for ${dept} (Sem ${sem})</option>`;
                    subjectSearchInput.placeholder = "No subjects found";
                }
            })
            .catch(err => {
                console.error("Failed to load subjects:", err);
                subjectSearchInput.placeholder = "Failed to load subjects";
            });
    }

    function renderSubjectOptions(subjects) {
        subjectSelect.innerHTML = "";
        subjects.forEach((sub, idx) => {
            const opt = document.createElement("option");
            opt.value = sub.subject_name;
            opt.textContent = `[${sub.subject_code}] ${sub.subject_name} (${sub.credits} Credits)`;
            opt.dataset.index = idx;
            subjectSelect.appendChild(opt);
        });
    }

    // Searchable Subject Filter
    subjectSearchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase().trim();
        const filtered = subjectCatalog.filter(sub => 
            sub.subject_name.toLowerCase().includes(query) ||
            sub.subject_code.toLowerCase().includes(query)
        );
        renderSubjectOptions(filtered);
    });

    // Subject Selection Event -> Update Information Card
    subjectSelect.addEventListener("change", function () {
        const selectedOption = this.options[this.selectedIndex];
        if (!selectedOption) return;

        const subName = selectedOption.value;
        const subObj = subjectCatalog.find(s => s.subject_name === subName);

        if (subObj) {
            infoCode.textContent = subObj.subject_code;
            infoName.textContent = subObj.subject_name;
            infoCredits.textContent = `${subObj.credits} Credits`;
            infoInternal.textContent = `${subObj.internal_marks} Marks`;
            infoExternal.textContent = `${subObj.external_marks} Marks`;

            infoDifficulty.textContent = subObj.difficulty;
            infoDifficulty.className = "badge-" + subObj.difficulty.toLowerCase();

            subjectInfoCard.classList.remove("d-none");
            step3Ind.classList.add("completed");
        }
    });

    function resetStep3() {
        subjectCatalog = [];
        subjectSearchInput.value = "";
        subjectSelect.innerHTML = "";
        subjectSelect.style.display = "none";
        subjectInfoCard.classList.add("d-none");
    }

    // -------------------------------------------------------------------------
    // ASSESSMENT STAGE SEGMENTED CONTROL
    // -------------------------------------------------------------------------
    stageOptions.forEach(opt => {
        opt.addEventListener("click", function () {
            stageOptions.forEach(o => o.classList.remove("active"));
            this.classList.add("active");

            const stageVal = this.getAttribute("data-stage");
            selectedStageInput.value = stageVal;

            if (stageVal === "Before Mid-1") {
                mid1Container.classList.add("d-none");
                mid2Container.classList.add("d-none");
                inputMid1.required = false;
                inputMid2.required = false;
            } else if (stageVal === "After Mid-1") {
                mid1Container.classList.remove("d-none");
                mid2Container.classList.add("d-none");
                inputMid1.required = true;
                inputMid2.required = false;
            } else if (stageVal === "After Mid-2") {
                mid1Container.classList.remove("d-none");
                mid2Container.classList.remove("d-none");
                inputMid1.required = true;
                inputMid2.required = true;
            }
        });
    });

});
