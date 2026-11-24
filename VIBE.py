# Danni Youngblood
# CIS261
# VIBE Coding

import csv
import os
import sys


DATA_FILE = "student_grades.txt"
TEST_NAMES = ("Test 1", "Test 2", "Test 3")
TEST_KEYS = ("test1", "test2", "test3")
LEGACY_CSV_FIELDS = ("id", "name", "test1", "test2", "test3")


def calculate_grade(average: float) -> str:
    """Return the letter grade for a numeric average."""
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def calculate_average(test1: float, test2: float, test3: float) -> float:
    return (test1 + test2 + test3) / 3


def get_student(students, student_id):
    """Find a student by ID, or return None if there is no match."""
    for student in students:
        if student["id"] == student_id:
            return student
    return None


def get_valid_score(test_name: str) -> float:
    while True:
        try:
            score = float(input(f"{test_name} score (0-100): "))
        except ValueError:
            print("Enter a number between 0 and 100.")
            continue

        if 0 <= score <= 100:
            return score
        print("Test score must be between 0 and 100.")


def create_student(
    name: str,
    student_id: str,
    test1: float,
    test2: float,
    test3: float,
):
    average: float = calculate_average(test1, test2, test3)
    grade: str = calculate_grade(average)
    return {
        "name": name,
        "id": student_id,
        "test1": test1,
        "test2": test2,
        "test3": test3,
        "average": average,
        "grade": grade,
    }


def add_student(students) -> bool:
    student_id: str = input("Student ID: ").strip()
    if not student_id:
        print("Student ID cannot be blank.")
        return False
    if get_student(students, student_id):
        print("A student with that ID already exists.")
        return False

    name: str = input("Student name: ").strip()
    if not name:
        print("Student name cannot be blank.")
        return False

    test1 = get_valid_score("Test 1")
    test2 = get_valid_score("Test 2")
    test3 = get_valid_score("Test 3")
    students.append(create_student(name, student_id, test1, test2, test3))
    print(f"Added {name}.")
    return True


def update_test_score(students) -> bool:
    student_id: str = input("Student ID: ").strip()
    student = get_student(students, student_id)
    if student is None:
        print("Student not found.")
        return False

    test_number = input("Which test score should be updated (1, 2, or 3)? ").strip()
    if test_number not in {"1", "2", "3"}:
        print("Choose test 1, 2, or 3.")
        return False

    test_name = f"Test {test_number}"
    student[f"test{test_number}"] = get_valid_score(test_name)
    student["average"] = calculate_average(
        student["test1"], student["test2"], student["test3"]
    )
    student["grade"] = calculate_grade(student["average"])
    print(f"Updated {test_name} for {student['name']}.")
    return True


def display_records(students) -> None:
    if not students:
        print("No student records found.")
        return

    headers = ("ID", "Name", "Test 1", "Test 2", "Test 3", "Average", "Grade")
    rows = []
    for student in students:
        rows.append(
            (
                student["id"],
                student["name"],
                *(f"{student[test_key]:.2f}" for test_key in TEST_KEYS),
                f"{student['average']:.2f}",
                student["grade"],
            )
        )

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    def format_row(row):
        return " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        )

    print("\nStudent Records")
    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(format_row(row))


def display_class_statistics(students) -> None:
    if not students:
        print("No student records are available for class statistics.")
        return

    highest = max(students, key=lambda student: student["average"])
    lowest = min(students, key=lambda student: student["average"])
    class_average = sum(
        student["average"] for student in students
    ) / len(students)

    print(f"Highest average: {highest['name']} ({highest['average']:.2f})")
    print(f"Lowest average: {lowest['name']} ({lowest['average']:.2f})")
    print(f"Class average: {class_average:.2f}")


def search_students(students) -> None:
    search_name = input("Enter a name to search for: ").strip().casefold()
    if not search_name:
        print("Search name cannot be blank.")
        return

    matches = [
        student
        for student in students
        if search_name in student["name"].casefold()
    ]
    if matches:
        display_records(matches)
    else:
        print("No matching students found.")


def load_legacy_students(file):
    file.seek(0)
    reader = csv.DictReader(file)
    if tuple(reader.fieldnames or ()) != LEGACY_CSV_FIELDS:
        raise ValueError(f"{DATA_FILE} uses an unsupported legacy format.")

    students = []
    for line_number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Invalid record on line {line_number}.")

        student_id = row["id"].strip()
        name = row["name"].strip()
        if not student_id or not name:
            raise ValueError(f"Student ID or name is blank on line {line_number}.")
        if get_student(students, student_id):
            raise ValueError(f"Duplicate student ID on line {line_number}.")

        try:
            scores = tuple(float(row[test_key]) for test_key in TEST_KEYS)
        except ValueError as error:
            raise ValueError(
                f"Invalid test score on line {line_number}."
            ) from error

        if any(not 0 <= score <= 100 for score in scores):
            raise ValueError(f"Test score out of range on line {line_number}.")
        students.append(create_student(name, student_id, *scores))

    return students


def load_pipe_students(file):
    students = []
    reader = csv.reader(file, delimiter="|")
    for line_number, row in enumerate(reader, start=1):
        if not row:
            continue
        if len(row) != 7:
            raise ValueError(f"Invalid record on line {line_number}.")

        name = row[0].strip()
        student_id = row[1].strip()
        if not student_id or not name:
            raise ValueError(f"Student ID or name is blank on line {line_number}.")
        if get_student(students, student_id):
            raise ValueError(f"Duplicate student ID on line {line_number}.")

        try:
            scores = tuple(float(row[index]) for index in range(2, 5))
        except ValueError as error:
            raise ValueError(
                f"Invalid test score on line {line_number}."
            ) from error

        if any(not 0 <= score <= 100 for score in scores):
            raise ValueError(f"Test score out of range on line {line_number}.")
        student = create_student(name, student_id, *scores)
        if row[5] != f"{student['average']:.2f}":
            raise ValueError(f"Invalid average on line {line_number}.")
        if row[6] != student["grade"]:
            raise ValueError(f"Invalid letter grade on line {line_number}.")
        students.append(student)

    return students


def load_students():
    try:
        file = open(DATA_FILE, newline="", encoding="utf-8")
    except FileNotFoundError:
        return []

    with file:
        first_line = file.readline()
        if first_line and tuple(next(csv.reader([first_line]))) == LEGACY_CSV_FIELDS:
            students = load_legacy_students(file)
            is_legacy = True
        else:
            file.seek(0)
            students = load_pipe_students(file)
            is_legacy = False

    if is_legacy:
        save_students(students)
        print("Converted saved records to the pipe-delimited format.")
    return students


def save_students(students) -> None:
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="|", lineterminator="\n")
        for student in students:
            writer.writerow(
                (
                    student["name"],
                    student["id"],
                    *(f"{student[test_key]:.2f}" for test_key in TEST_KEYS),
                    f"{student['average']:.2f}",
                    student["grade"],
                )
            )


def save_with_message(students) -> None:
    try:
        save_students(students)
    except OSError as error:
        print(f"Could not save records to {DATA_FILE}: {error}")
    else:
        print(f"Records saved to {DATA_FILE}.")


def get_menu_choice() -> str:
    prompt = "Choose 1-5, or press ESC to exit: "
    if not sys.stdin.isatty():
        choice = input(prompt).strip()
        return "ESC" if choice.casefold() in {"esc", "\x1b"} else choice

    print(prompt, end="", flush=True)
    if os.name == "nt":
        import msvcrt

        character = msvcrt.getwch()
    else:
        import termios
        import tty

        file_descriptor = sys.stdin.fileno()
        previous_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            character = sys.stdin.read(1)
        finally:
            termios.tcsetattr(
                file_descriptor, termios.TCSADRAIN, previous_settings
            )

    print()
    return "ESC" if character == "\x1b" else character.strip()


def main() -> None:
    try:
        students = load_students()
    except (OSError, ValueError, csv.Error) as error:
        print(f"Could not load records from {DATA_FILE}: {error}")
        return

    print(f"Loaded {len(students)} student record(s).")
    while True:
        print("\nStudent Record Manager")
        print("1. Add student and test scores")
        print("2. Update a test score")
        print("3. Display all students")
        print("4. Display class statistics")
        print("5. Search for a student by name")

        choice = get_menu_choice()
        if choice == "ESC":
            save_with_message(students)
            print("Goodbye.")
            break
        if choice == "1":
            if add_student(students):
                save_with_message(students)
        elif choice == "2":
            if update_test_score(students):
                save_with_message(students)
        elif choice == "3":
            display_records(students)
        elif choice == "4":
            display_class_statistics(students)
        elif choice == "5":
            search_students(students)
        else:
            print("Invalid option. Choose 1, 2, 3, 4, or 5, or press ESC.")


if __name__ == "__main__":
    main()
class S:
    ...

S