from agentic_app.tools.calculator import calculate_grade


def test_grade_boundaries():
    """Exact boundary values must land in the higher grade."""
    assert calculate_grade(80) == "A"
    assert calculate_grade(79) == "B"
    assert calculate_grade(70) == "B"
    assert calculate_grade(69) == "C"
    assert calculate_grade(60) == "C"
    assert calculate_grade(59) == "D"
    assert calculate_grade(50) == "D"
    assert calculate_grade(49) == "F"
