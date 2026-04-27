class School:
    def __init__(self):
        self._roster = {}  # grade -> list of students
        self._added_status = []  # track if each student was successfully added
        self._student_grades = {}  # student name -> grade (to prevent duplicates)
    
    def add_student(self, name, grade):
        # Check if student already exists in any grade
        if name in self._student_grades:
            self._added_status.append(False)
            return False
        
        # Add student to grade
        if grade not in self._roster:
            self._roster[grade] = []
        
        self._roster[grade].append(name)
        self._student_grades[name] = grade
        self._added_status.append(True)
        return True
    
    def roster(self):
        # Sort grades numerically
        sorted_grades = sorted(self._roster.keys())
        result = []
        
        for grade in sorted_grades:
            # Sort students in grade alphabetically
            sorted_students = sorted(self._roster[grade])
            result.extend(sorted_students)
        
        return result
    
    def grade(self, grade_number):
        # Return students in specific grade sorted alphabetically
        if grade_number not in self._roster:
            return []
        
        return sorted(self._roster[grade_number])
    
    def added(self):
        # Return the list of added status
        return self._added_status