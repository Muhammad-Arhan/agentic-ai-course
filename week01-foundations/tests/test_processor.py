from agentic_app.services.processor import Student, format_report


def test_report_contains_student_details():
    report = format_report(Student("Ali", 85, "A"))
    assert "Name: Ali" in report
    assert "Marks: 85" in report
    assert "Grade: A" in report
