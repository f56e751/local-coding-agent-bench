# Task: grade-school

Implement the solution in `grade_school.py` so that every test in `grade_school_test.py` passes.

## Problem description

# Instructions

Given students' names along with the grade that they are in, create a roster for the school.

In the end, you should be able to:

- Add a student's name to the roster for a grade
  - "Add Jim to grade 2."
  - "OK."
- Get a list of all students enrolled in a grade
  - "Which students are in grade 2?"
  - "We've only got Jim just now."
- Get a sorted list of all students in all grades.
  Grades should sort as 1, 2, 3, etc., and students within a grade should be sorted alphabetically by name.
  - "Who all is enrolled in school right now?"
  - "Let me think.
    We have Anna, Barb, and Charlie in grade 1, Alex, Peter, and Zoe in grade 2 and Jim in grade 5.
    So the answer is: Anna, Barb, Charlie, Alex, Peter, Zoe and Jim"

Note that all our students only have one name (It's a small town, what do you want?) and each student cannot be added more than once to a grade or the roster.
In fact, when a test attempts to add the same student more than once, your implementation should indicate that this is incorrect.


# Instructions append

The tests for this exercise expect your school roster will be implemented via a School `class` in Python.
If you are unfamiliar with classes in Python, [classes][classes in python] from the Python docs is a good place to start.

[classes in python]: https://docs.python.org/3/tutorial/classes.html


## Files

- Starter: `grade_school.py`  (edit this)
- Tests:   `grade_school_test.py`  (do NOT edit; used for grading)

## Rules

- Only modify `grade_school.py`.  Do not edit the tests or create new files.
- Python stdlib only — no package installs.
- When you believe you are done, run `pytest grade_school_test.py -x -q` and confirm green.
