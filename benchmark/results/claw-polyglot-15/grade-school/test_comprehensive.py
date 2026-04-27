#!/usr/bin/env python3

from grade_school import School

# Test specific examples from the test suite
print("=== Testing specific examples ===")

# Test the sorting functionality
school = School()
school.add_student("Peter", 2)
school.add_student("Anna", 1)
school.add_student("Barb", 1)
school.add_student("Zoe", 2)
school.add_student("Alex", 2)
school.add_student("Jim", 3)
school.add_student("Charlie", 1)

print("Roster:", school.roster())
print("Expected: ['Anna', 'Barb', 'Charlie', 'Alex', 'Peter', 'Zoe', 'Jim']")
print("Match:", school.roster() == ['Anna', 'Barb', 'Charlie', 'Alex', 'Peter', 'Zoe', 'Jim'])

print("\nGrade 1 students:", school.grade(1))
print("Expected: ['Anna', 'Barb', 'Charlie']")
print("Match:", school.grade(1) == ['Anna', 'Barb', 'Charlie'])

print("\nGrade 2 students:", school.grade(2))
print("Expected: ['Alex', 'Peter', 'Zoe']")
print("Match:", school.grade(2) == ['Alex', 'Peter', 'Zoe'])

print("\nGrade 3 students:", school.grade(3))
print("Expected: ['Jim']")
print("Match:", school.grade(3) == ['Jim'])

# Test duplicate prevention
print("\n=== Testing duplicate prevention ===")
school2 = School()
school2.add_student("Blair", 2)
school2.add_student("James", 2)
school2.add_student("James", 2)  # duplicate
school2.add_student("Paul", 2)

print("Added status:", school2.added())
print("Expected: [True, True, False, True]")
print("Match:", school2.added() == [True, True, False, True])

print("Roster:", school2.roster())
print("Expected: ['Blair', 'James', 'Paul']")
print("Match:", school2.roster() == ['Blair', 'James', 'Paul'])

print("\n=== All tests completed ===")