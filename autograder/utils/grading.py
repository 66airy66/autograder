# Minimal grading stub. Return a score from SQL text and question_id.
# Replace with real grading logic later.
def grade_submission(submitted_sql: str, question_id: int) -> int:
    # TODO: implement actual grading rules/test cases
    # For now: 0 for empty, 100 otherwise (example)
    submitted_sql = (submitted_sql or "").strip()
    return 100 if submitted_sql else 0