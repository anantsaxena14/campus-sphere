import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def chat_with_ai(message: str, mode: str = 'normal', user_context: dict = None) -> str:
    """
    Chat with Gemini AI based on the selected mode
    """
    try:
        if mode == 'normal':
            system_prompt = """You are a friendly and helpful virtual teacher assistant for a campus management system. 
            Provide clear, concise answers to student questions.
            
            IMPORTANT: If the user's message includes [Database Information], use that real data from the campus database to answer their questions accurately. 
            For example, if they ask about events and you see event data, tell them about those specific events with dates and details.
            Always prioritize database information over general knowledge when answering campus-specific questions."""
        elif mode == 'practice':
            system_prompt = """You are a practice mode assistant. When asked for practice questions:
            - Generate coding problems with clear descriptions
            - Create MCQs with 4 options
            - Provide subjective questions for deeper understanding
            - Include test cases for coding problems
            Do NOT reveal answers until the student submits their solution."""
        elif mode == 'counseling':
            user_info = ""
            if user_context:
                user_info = f"Student Info: {user_context.get('name', 'Student')}, Course: {user_context.get('course', 'N/A')}, Year: {user_context.get('year', 'N/A')}"
            system_prompt = f"""You are a supportive career counselor and mentor for college students. 
            {user_info}
            Provide personalized guidance, motivation, and career advice. Be empathetic and encouraging.
            If database information is provided about clubs, faculty, alumni, or resources, use it to give specific recommendations."""
        else:
            system_prompt = "You are a helpful virtual teacher assistant."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=message)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7
            )
        )
        
        return response.text or "I'm sorry, I couldn't generate a response. Please try again."
    
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"


def generate_practice_questions(subject: str, question_type: str, difficulty: str = 'medium') -> dict:
    """
    Generate practice questions using Gemini
    """
    try:
        if question_type == 'coding':
            prompt = f"""Generate a {difficulty} level coding question for {subject}.
            Return JSON with: {{"question": "description", "test_cases": [{{"input": "", "output": ""}}], "hints": []}}"""
        elif question_type == 'mcq':
            prompt = f"""Generate a {difficulty} level multiple choice question for {subject}.
            Return JSON with: {{"question": "question text", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": ""}}"""
        else:
            prompt = f"""Generate a {difficulty} level subjective question for {subject}.
            Return JSON with: {{"question": "question text", "key_points": [], "sample_answer": ""}}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8
            )
        )
        
        if response.text:
            return json.loads(response.text)
        return {"error": "Could not generate question"}
    
    except Exception as e:
        return {"error": str(e)}


def check_coding_answer(question: str, user_code: str, test_cases: list) -> dict:
    """
    Check coding answer using Gemini
    """
    try:
        prompt = f"""Question: {question}
        
        User's Code:
        ```
        {user_code}
        ```
        
        Test Cases: {json.dumps(test_cases)}
        
        Analyze if the code solves the problem correctly. Return JSON with:
        {{"correct": true/false, "feedback": "detailed feedback", "passed_tests": number, "total_tests": number}}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
        return {"error": "Could not evaluate answer"}
    
    except Exception as e:
        return {"error": str(e)}
