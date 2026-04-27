#!/usr/bin/env python3

from grade_school import School

# Test basic functionality
school = School()
print("Testing basic functionality...")

# Test 1: Empty roster
print("1. Empty roster:", school.roster())

# Test 2: Add a student
result = school.add_student("Aimee", 2)
print("2. Add Aimee to grade 2:", result)
print("   Added status:", school.added())
print("   Roster:", school.roster())

# Test 3: Add multiple students to same grade
school.add_student("Blair", 2)
school.add_student("James", 2)
print("3. Add multiple students to grade 2")
print("   Added status:", school.added())
print("   Roster:", school.roster())

# Test 4: Try adding duplicate student
result = school.add_student("James", 2)
print("4. Try adding duplicate James to grade 2:", result)
print("   Added status:", school.added())
print("   Roster:", school.roster())

# Test 5: Get grade
print("5. Students in grade 2:", school.grade(2))
print("   Students in grade 1:", school.grade(1))

# Test 6: Add students to different grades
school.add_student("Chelsea", 3)
school.add_student("Logan", 7)
print("6. Add students to different grades")
print("   Added status:", school.added())
print("   Roster:", school.roster())

# Test 7: Test sorting
school2 = School()
school2.add_student("Jim", 3)
school2.add_student("Peter", 2)
school2.add_student("Anna", 1)
print("7. Test sorting")
print("   Roster:", school2.roster())

print("All tests completed!")