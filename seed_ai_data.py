from app import app, db
from models import PracticeQuestion
import json

with app.app_context():
    sample_questions = [
        PracticeQuestion(
            question="Write a Python function to check if a number is prime.",
            question_type="coding",
            options=None,
            correct_answer="def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
            test_cases=json.dumps([
                {"input": "7", "output": "True"},
                {"input": "10", "output": "False"},
                {"input": "13", "output": "True"}
            ]),
            difficulty="easy",
            subject="Python Programming"
        ),
        PracticeQuestion(
            question="What is the time complexity of binary search?",
            question_type="mcq",
            options=json.dumps(["O(n)", "O(log n)", "O(n^2)", "O(1)"]),
            correct_answer="O(log n)",
            test_cases=None,
            difficulty="medium",
            subject="Data Structures"
        ),
        PracticeQuestion(
            question="Write a function to reverse a linked list.",
            question_type="coding",
            options=None,
            correct_answer="def reverse_list(head):\n    prev = None\n    current = head\n    while current:\n        next_node = current.next\n        current.next = prev\n        prev = current\n        current = next_node\n    return prev",
            test_cases=json.dumps([
                {"input": "[1,2,3,4,5]", "output": "[5,4,3,2,1]"},
                {"input": "[1,2]", "output": "[2,1]"}
            ]),
            difficulty="medium",
            subject="Data Structures"
        ),
        PracticeQuestion(
            question="Which HTTP method is used to update a resource?",
            question_type="mcq",
            options=json.dumps(["GET", "POST", "PUT", "DELETE"]),
            correct_answer="PUT",
            test_cases=None,
            difficulty="easy",
            subject="Web Development"
        ),
        PracticeQuestion(
            question="Explain the concept of inheritance in Object-Oriented Programming.",
            question_type="subjective",
            options=None,
            correct_answer="Inheritance is a mechanism where a new class (derived/child class) inherits properties and methods from an existing class (base/parent class). It promotes code reusability and establishes a relationship between classes.",
            test_cases=None,
            difficulty="medium",
            subject="Object-Oriented Programming"
        )
    ]
    
    for question in sample_questions:
        existing = PracticeQuestion.query.filter_by(question=question.question).first()
        if not existing:
            db.session.add(question)
    
    db.session.commit()
    print(f"Added {len(sample_questions)} sample practice questions!")
