"""Phase 03 - Tasks 11-12: JSON objects and arrays as Python dictionaries and lists.

Run from the week02-api-integration folder:
    python lab/phase03/json_basics.py
"""

import json


def task_11_json_object():
    print("=== Task 11: JSON object -> Python dictionary ===")

    # The same data as JSON text...
    json_text = '{"name": "Ali", "marks": 85, "program": "BSCS"}'

    # ...and as a Python dictionary. json.loads() converts one into the other.
    student = json.loads(json_text)

    print(f"Name: {student['name']}")
    print(f"Marks: {student['marks']}")
    print(f"Program: {student['program']}")

    # json.dumps() goes the other way: Python dictionary -> JSON text.
    print("Back to JSON text:", json.dumps(student))


def task_12_json_array():
    print("\n=== Task 12: JSON array -> Python list of dictionaries ===")

    students = [
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Sara"},
        {"id": 3, "name": "Ahmed"},
    ]

    for student in students:
        print(f"ID: {student['id']}")
        print(f"Name: {student['name']}")
        print()


if __name__ == "__main__":
    task_11_json_object()
    task_12_json_array()
