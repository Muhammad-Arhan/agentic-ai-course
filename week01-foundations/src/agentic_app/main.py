"""Application entry point.

Run from the project root:
    PYTHONPATH=src python -m agentic_app.main           (type name and marks)
    PYTHONPATH=src python -m agentic_app.main --json    (load data/student.json)
"""

import argparse
import sys

from agentic_app.config import APP_NAME, DEBUG
from agentic_app.logger import logger
from agentic_app.services.processor import (
    Student,
    display_report,
    load_student_data,
)
from agentic_app.tools.calculator import calculate_grade
from agentic_app.utils.validation import validate_marks, validate_name


def run_from_json():
    data = load_student_data()
    if data is None:
        return 1

    print("Student Information")
    print("-------------------")
    print(f"ID: {data['id']}")
    print(f"Name: {data['name']}")
    print(f"Program: {data['program']}")
    print(f"Semester: {data['semester']}")
    print(f"Marks: {data['marks']}")

    student = Student(data["name"], data["marks"], calculate_grade(data["marks"]))
    display_report(student)
    logger.info("Report generated from JSON data")
    return 0


def run_interactive():
    name = input("Enter student name: ")
    if not validate_name(name):
        logger.warning("Empty student name entered")
        print("Error: Name cannot be empty.")
        return 1

    try:
        marks = int(input("Enter student marks: "))
    except ValueError:
        logger.error("Invalid marks entered")
        print("Error: Marks must be a number.")
        return 1

    if not validate_marks(marks):
        logger.warning(f"Invalid marks entered: {marks}")
        print("Error: Marks must be between 0 and 100.")
        return 1

    student = Student(name, marks, calculate_grade(marks))
    display_report(student)
    logger.info(f"Report generated for {name}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Student Information System")
    parser.add_argument(
        "--json", action="store_true", help="load the student from data/student.json"
    )
    args = parser.parse_args()

    logger.info("Application started")
    print(f"Starting: {APP_NAME}")
    print(f"Debug Mode: {DEBUG}")
    print()

    return run_from_json() if args.json else run_interactive()


if __name__ == "__main__":
    sys.exit(main())
