#!/usr/bin/env python3

from grade_school import School

# Test the multi-grade duplicate prevention
print("=== Testing multi-grade duplicate prevention ===")

school = School()
school.add_student("Blair", 2)
school.add_student("James", 2)
school.add_student("James", 3)  # Trying to add James to different grade
school.add_student("Paul", 3)

print("Added status:", school.added())
print("Expected: [True, True, False, True]")
print("Match:", school.added() == [True, True, False, True])

print("Roster:", school.roster())
print("Expected: ['Blair', 'James', 'Paul']")
print("Match:", school.roster() == ['Blair', 'James', 'Paul'])

print("Grade 2 students:", school.grade(2))
print("Expected: ['Blair', 'James']")
print("Match:", school.grade(2) == ['Blair', 'James'])

print("Grade 3 students:", school.grade(3))
print("Expected: ['Paul']")
print("Match:", school.grade(3) == ['Paul'])

print("\n=== Test completed ===")