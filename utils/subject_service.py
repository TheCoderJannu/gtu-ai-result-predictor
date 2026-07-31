from database import (
    get_all_departments,
    get_all_semesters,
    get_subject_by_code,
    get_subject_by_name,
    get_subjects_by_dept_and_sem,
)


class SubjectService:
    """Service layer for retrieving and validating GTU departments, semesters, and subjects."""

    @staticmethod
    def list_departments():
        """Returns list of distinct GTU departments."""
        return get_all_departments()

    @staticmethod
    def list_semesters():
        """Returns list of supported GTU semesters (1 to 8)."""
        return get_all_semesters()

    @staticmethod
    def get_subjects(department, semester):
        """Retrieve subjects matching department and semester."""
        if not department or not semester:
            return []
        try:
            sem_num = int(semester)
            if sem_num < 1 or sem_num > 8:
                return []
        except ValueError:
            return []

        return get_subjects_by_dept_and_sem(department, sem_num)

    @staticmethod
    def get_subject_info_by_code(subject_code):
        """Retrieve subject details by subject code."""
        if not subject_code:
            return None
        return get_subject_by_code(str(subject_code).strip())

    @staticmethod
    def get_subject_info(department, semester, subject_name_or_code):
        """Retrieve subject details by name/code in department and semester."""
        if not department or not semester or not subject_name_or_code:
            return None
        return get_subject_by_name(
            department, int(semester), str(subject_name_or_code).strip()
        )
