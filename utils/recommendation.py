class RecommendationEngine:
    """
    Generates tailored GTU subject revision topic recommendations,
    strengths analysis, and weakness highlights based on student parameters.
    """

    # Domain topic dictionary for GTU subjects
    SUBJECT_TOPICS = {
        "Operating System": [
            "CPU Scheduling Algorithms (FCFS, SJF, Round Robin)",
            "Banker's Deadlock Avoidance and Prevention",
            "Page Replacement Policies (FIFO, LRU, Optimal)",
            "Process Synchronization & Semaphores",
            "Virtual Memory & Demand Paging concepts",
        ],
        "Web Technology": [
            "RESTful API design and JSON serialization",
            "DOM Manipulation and Event Handling in JavaScript",
            "CSS Flexbox, Grid Layouts & Responsive Design",
            "Asynchronous JavaScript (Promises, Async/Await)",
            "Client-side Form Validation & HTTP Methods",
        ],
        "Theory of Computation": [
            "Deterministic & Non-Deterministic Finite Automata (DFA/NFA)",
            "Context-Free Grammars (CFG) and Chomsky Normal Form",
            "Pushdown Automata (PDA) design",
            "Turing Machine construction and Halting Problem",
            "P vs NP Complexity Classes and Decidability",
        ],
        "Advanced Java Programming": [
            "JDBC Database Connectivity & PreparedStatement",
            "Servlet Lifecycle and Request/Response Dispatching",
            "JSP Directives, Scriptlets, and Expression Language",
            "Java Collections Framework (Map, Set, List implementations)",
            "Multithreading & Thread Synchronization",
        ],
        "Data Structures": [
            "AVL Tree Rotations and Tree Traversals (Inorder/Preorder/Postorder)",
            "Graph Algorithms (Dijkstra, BFS, DFS, Minimum Spanning Trees)",
            "Dynamic Programming (0/1 Knapsack, Longest Common Subsequence)",
            "Stack & Queue applications (Infix to Postfix conversion)",
            "Hashing Techniques and Collision Resolution Strategies",
        ],
        "Database Management Systems": [
            "Relational Algebra & Advanced SQL Joins",
            "Database Normalization (1NF, 2NF, 3NF, BCNF)",
            "Transaction Processing & ACID Properties",
            "B-Trees and B+ Trees Indexing Mechanisms",
            "Concurrency Control Protocols (Two-Phase Locking)",
        ],
        "Computer Networks": [
            "IPv4/IPv6 Subnetting & CIDR calculations",
            "TCP/IP 3-Way Handshake & Congestion Control",
            "Routing Protocols (OSPF, RIP, BGP)",
            "OSI Layer Architecture and Packet Encapsulation",
            "DNS, HTTP/HTTPS, and DHCP Protocol operations",
        ],
        "Analysis & Design of Algorithms": [
            "Asymptotic Notations (Big-O, Omega, Theta)",
            "Divide and Conquer (Merge Sort, Quick Sort analysis)",
            "Greedy Algorithms (Fractional Knapsack, Huffman Coding)",
            "Dynamic Programming & Backtracking (N-Queens problem)",
            "NP-Completeness and Polynomial Time Reductions",
        ],
        "Compiler Design": [
            "Lexical Analysis and Finite Automata construction",
            "LL(1) and LR(1) Parsing Table Generation",
            "Syntax Directed Translation (SDT) & Intermediate Code",
            "Code Optimization (Loop Invariants, Common Subexpressions)",
            "Register Allocation & Symbol Table Management",
        ],
        "Machine Learning": [
            "Supervised vs Unsupervised Learning algorithms",
            "Linear & Logistic Regression mathematical formulations",
            "Decision Trees, Random Forests, and Gradient Boosting",
            "Overfitting Prevention (Regularization L1/L2, Cross-Validation)",
            "Evaluation Metrics (Confusion Matrix, ROC-AUC, F1-Score)",
        ],
        "Engineering Thermodynamics": [
            "First & Second Laws of Thermodynamics calculations",
            "Carnot Engine Efficiency & Entropy change equations",
            "Rankine Cycle & Steam Power Plant analysis",
            "Properties of Pure Substances & Steam Tables usage",
            "Gas Power Cycles (Otto, Diesel, Dual Cycles)",
        ],
        "Fluid Mechanics & Hydraulic Machines": [
            "Bernoulli's Equation & Venturimeter numericals",
            "Fluid Statics & Buoyancy Force calculations",
            "Navier-Stokes Equations & Laminar/Turbulent Pipe Flow",
            "Pelton Wheel & Francis Turbine efficiency equations",
            "Boundary Layer Thickness & Drag Force analysis",
        ],
        "Concrete Technology": [
            "Concrete Mix Design Procedure (IS 10262 Standard)",
            "Water-Cement Ratio influence on Compressive Strength",
            "Workability Tests (Slump Cone, Compacting Factor)",
            "Curing Methods & Admixtures in Concrete",
            "Non-Destructive Testing (Rebound Hammer, Ultrasonic Pulse)",
        ],
        "Mechanics of Solids": [
            "Shear Force & Bending Moment Diagrams for Beams",
            "Stress & Strain Relationship (Hooke's Law, Young's Modulus)",
            "Torsion of Circular Shafts & Polar Moment of Inertia",
            "Mohr's Circle for Principal Stresses",
            "Euler's Column Buckling Theory",
        ],
        "Electrical Circuit Analysis": [
            "Kirchhoff's Laws (KVL/KCL) & Mesh/Nodal Analysis",
            "Network Theorems (Thevenin, Norton, Superposition)",
            "Transient Analysis of RL, RC, and RLC Circuits",
            "Resonance in Series & Parallel AC Circuits",
            "Two-Port Network Parameters (Z, Y, ABCD Parameters)",
        ],
        "Electrical Power System-1": [
            "Transmission Line Performance & Voltage Regulation",
            "Sag and Tension Calculations in Overhead Lines",
            "Insulators & Underground Cable Capacitance",
            "Corona Effect & Power Loss Factors",
            "Per-Unit System & Single Line Diagram representation",
        ],
        "Digital Electronics": [
            "Boolean Algebra & Karnaugh Map (K-Map) Simplifications",
            "Combinational Circuits (Multiplexer, Decoder, Adder)",
            "Sequential Circuits (Flip-Flops: JK, D, T, SR)",
            "Counter Design (Synchronous & Asynchronous)",
            "Analog-to-Digital (ADC) & Digital-to-Analog (DAC) Converters",
        ],
        "VLSI Design": [
            "CMOS Inverter Characteristics & VTC Curve",
            "MOSFET Physics, Threshold Voltage, & Drain Current",
            "CMOS Logic Gate Layout Design Rules",
            "Verilog HDL Hardware Description & Testbenches",
            "Static & Dynamic Power Dissipation in Integrated Circuits",
        ],
    }

    @classmethod
    def get_subject_recommendations(cls, subject_name):
        """Retrieve topic recommendations tailored to subject name."""
        if not subject_name:
            return cls._default_recommendations("Selected Subject")

        # Exact match lookup
        for key, topics in cls.SUBJECT_TOPICS.items():
            if key.lower() in subject_name.lower() or subject_name.lower() in key.lower():
                return topics

        # Generic GTU subject fallback topics
        return cls._default_recommendations(subject_name)

    @staticmethod
    def _default_recommendations(subject_name):
        """Fallback recommendation structure for unlisted subjects."""
        return [
            f"Review core GTU mid-semester question papers for {subject_name}.",
            f"Solve numerical problems from past 5 years of GTU end-sem examinations.",
            f"Focus on high-weightage theoretical units in the GTU syllabus.",
            f"Prepare clear block diagrams, derivations, and structural charts.",
            f"Conduct timed practice for 70-mark GTU theory paper pattern.",
        ]

    @staticmethod
    def analyze_strengths_and_weaknesses(data):
        """
        Analyzes student academic parameters and generates bulleted lists of
        strengths and weaknesses.
        """
        strengths = []
        weaknesses = []

        attendance = float(data.get("attendance_pct", 0))
        spi = float(data.get("spi_last_sem", 0))
        study_hours = float(data.get("weekly_study_hours", 0))
        backlogs = int(data.get("active_backlogs", 0))
        stage = data.get("assessment_stage", "")
        mid1 = data.get("mid1_marks")
        mid2 = data.get("mid2_marks")

        # Attendance Analysis
        if attendance >= 85.0:
            strengths.append(
                f"Excellent attendance record ({attendance:.1f}%), exceeding the GTU 75% threshold."
            )
        elif attendance >= 75.0:
            strengths.append(
                f"Good classroom attendance ({attendance:.1f}%), meeting GTU mandatory criteria."
            )
        else:
            weaknesses.append(
                f"Low attendance ({attendance:.1f}%), below GTU's 75% requirement. Detainment risk."
            )

        # SPI Analysis
        if spi >= 8.0:
            strengths.append(
                f"Outstanding previous academic record with Last Sem SPI of {spi:.2f}."
            )
        elif spi >= 6.5:
            strengths.append(
                f"Consistent academic foundation with Last Sem SPI of {spi:.2f}."
            )
        elif spi < 5.5:
            weaknesses.append(
                f"Low previous SPI ({spi:.2f}) indicates potential gaps in fundamental concepts."
            )

        # Study Hours Analysis
        if study_hours >= 20.0:
            strengths.append(
                f"Strong weekly study routine ({study_hours:.1f} hrs/week) dedicated to preparation."
            )
        elif study_hours < 12.0:
            weaknesses.append(
                f"Low weekly study time ({study_hours:.1f} hrs/week). Recommend increasing to 16+ hrs/week."
            )

        # Backlog Analysis
        if backlogs == 0:
            strengths.append("Zero active GTU backlogs, allowing 100% focus on current semester subjects.")
        elif backlogs >= 2:
            weaknesses.append(
                f"Has {backlogs} active GTU backlogs, adding exam stress and reducing preparation time."
            )
        else:
            weaknesses.append(f"Carrying {backlogs} active backlog. Clear backlogs to boost SPI.")

        # Mid-1 Analysis if applicable
        if stage in ["After Mid-1", "After Mid-2"] and mid1 is not None:
            mid1_val = float(mid1)
            if mid1_val >= 7.5:
                strengths.append(f"Strong Mid-1 performance ({mid1_val:.1f}/10 marks).")
            elif mid1_val < 5.0:
                weaknesses.append(f"Below average Mid-1 performance ({mid1_val:.1f}/10 marks).")

        # Mid-2 Analysis if applicable
        if stage == "After Mid-2" and mid2 is not None:
            mid2_val = float(mid2)
            if mid2_val >= 15.0:
                strengths.append(f"High Mid-2 score ({mid2_val:.1f}/20 marks).")
            elif mid2_val < 10.0:
                weaknesses.append(f"Low Mid-2 score ({mid2_val:.1f}/20 marks). Re-study key modules.")

        # Ensure at least 1 default strength and weakness
        if not strengths:
            strengths.append("Maintains steady engagement with course materials.")
        if not weaknesses:
            weaknesses.append("No major academic risks detected. Maintain current study routine.")

        return {"strengths": strengths, "weaknesses": weaknesses}
