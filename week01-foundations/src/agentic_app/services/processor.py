"""Student data handling and report generation."""

import json

from agentic_app.config import DATA_FILE
from agentic_app.logger import logger


class Student:
    def __init__(self, name, marks, grade):
        self.name = name
        self.marks = marks
        self.grade = grade

    def get_details(self):
        return {
            "name": self.name,
            "marks": self.marks,
            "grade": self.grade,
        }


def load_student_data(path=DATA_FILE):
    """Read student data from a JSON file. Returns a dict, or None on failure."""
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Student file not found: {path}")
        print("Error: Student file not found.")
    except json.JSONDecodeError:
        logger.error(f"Student file contains invalid JSON: {path}")
        print("Error: Student file is not valid JSON.")
    return None


def format_report(student):
    return (
        "\nStudent Report\n"
        "----------------\n"
        f"Name: {student.name}\n"
        f"Marks: {student.marks}\n"
        f"Grade: {student.grade}"
    )


def display_report(student):
    print(format_report(student))
