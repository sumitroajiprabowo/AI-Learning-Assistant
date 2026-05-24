"""
Quiz Generator Module - Milestone 4
Implements dynamic MCQ generation based on difficulty levels
Creates relevant and challenging questions
"""

import json
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime
from config import Config
from .qa_system import QASystem

class QuizGenerator:
    """Generate interactive quizzes with multiple choice questions"""
    
    def __init__(self):
        self.qa_system = QASystem()
        self.difficulty_weights = {
            'easy': {'basic': 0.7, 'intermediate': 0.3, 'advanced': 0.0},
            'medium': {'basic': 0.3, 'intermediate': 0.5, 'advanced': 0.2},
            'hard': {'basic': 0.1, 'intermediate': 0.3, 'advanced': 0.6}
        }
    
    def generate_quiz(self, quiz_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete quiz based on configuration
        
        Args:
            quiz_config (dict): {
                'subject': str - Subject for the quiz
                'topic': str - Specific topic (optional)
                'difficulty': str - 'easy', 'medium', 'hard'
                'num_questions': int - Number of questions
                'question_types': List[str] - Types of questions to include
            }
            
        Returns:
            dict: Complete quiz with questions, answers, and metadata
        """
        try:
            # Validate configuration
            validation = self._validate_quiz_config(quiz_config)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error'],
                    'quiz': None
                }
            
            # Extract parameters
            subject = quiz_config.get('subject', '').strip()
            topic = quiz_config.get('topic', '').strip()
            difficulty = quiz_config.get('difficulty', 'medium')
            num_questions = quiz_config.get('num_questions', Config.DEFAULT_QUIZ_LENGTH)
            question_types = quiz_config.get('question_types', ['multiple_choice'])
            
            # Generate quiz ID and metadata
            quiz_id = str(uuid.uuid4())
            created_date = datetime.now().isoformat()
            
            # Generate questions
            questions = []
            for i in range(num_questions):
                question = self._generate_single_question(
                    subject, topic, difficulty, i + 1, question_types
                )
                if question:
                    questions.append(question)
            
            if not questions:
                return {
                    'success': False,
                    'error': 'Failed to generate any questions',
                    'quiz': None
                }
            
            # Create quiz structure
            quiz = {
                'id': quiz_id,
                'created_date': created_date,
                'metadata': {
                    'subject': subject,
                    'topic': topic,
                    'difficulty': difficulty,
                    'num_questions': len(questions),
                    'estimated_time_minutes': len(questions) * 2,
                    'question_types': question_types
                },
                'questions': questions,
                'scoring': {
                    'total_points': len(questions),
                    'passing_score': max(1, len(questions) * 0.6),
                    'grading_scale': self._get_grading_scale()
                },
                'instructions': self._generate_instructions(difficulty),
                'completed': False,
                'results': None
            }
            
            return {
                'success': True,
                'quiz': quiz,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating quiz: {str(e)}',
                'quiz': None
            }
    
    def _validate_quiz_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quiz configuration"""
        if not isinstance(config, dict):
            return {'valid': False, 'error': 'Configuration must be a dictionary'}
        
        # Check required fields
        if not config.get('subject'):
            return {'valid': False, 'error': 'Subject is required'}
        
        # Validate difficulty
        difficulty = config.get('difficulty', 'medium')
        if difficulty not in Config.DIFFICULTY_LEVELS:
            return {'valid': False, 'error': f'Difficulty must be one of: {Config.DIFFICULTY_LEVELS}'}
        
        # Validate number of questions
        num_questions = config.get('num_questions', Config.DEFAULT_QUIZ_LENGTH)
        if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 50:
            return {'valid': False, 'error': 'Number of questions must be between 1 and 50'}
        
        return {'valid': True, 'error': None}
    
    def _generate_single_question(self, subject: str, topic: str, difficulty: str, 
                                question_num: int, question_types: List[str]) -> Dict:
        """Generate a single quiz question"""
        try:
            # Select question type
            question_type = random.choice(question_types)
            
            if question_type == 'multiple_choice':
                return self._generate_mcq(subject, topic, difficulty, question_num)
            elif question_type == 'true_false':
                return self._generate_true_false(subject, topic, difficulty, question_num)
            else:
                return self._generate_mcq(subject, topic, difficulty, question_num)
                
        except Exception as e:
            # Return fallback question
            return self._generate_fallback_question(subject, difficulty, question_num)
    
    def _generate_mcq(self, subject: str, topic: str, difficulty: str, question_num: int) -> Dict:
        """Generate a multiple choice question using AI"""
        try:
            context = f"Subject: {subject}"
            if topic:
                context += f", Topic: {topic}"
            # For Gemini provider, request strictly-formatted JSON output to include correct answers
            prompt = {
                "instruction": (
                    f"Generate a {difficulty} multiple choice question for {subject}. "
                    f"If a topic is provided, focus on: {topic}. "
                    "Return ONLY a valid JSON object with this exact schema: "
                    "{\"question\": \"...\", \"options\": [\"...\", \"...\", \"...\", \"...\"], \"correct\": 0, \"explanation\": \"...\"}. "
                    "Do not add markdown, bullet points, numbering, or extra text. "
                    "The value of correct must be the zero-based index of the correct option."
                )
            }

            # Use the QASystem to ask Gemini specifically
            response = self.qa_system.ask_question(prompt, context, provider="gemini")

            if response.get('success'):
                # Expect response['answer'] to be JSON string or dict
                ans = response.get('answer')
                try:
                    if isinstance(ans, str):
                        parsed = json.loads(ans)
                    elif isinstance(ans, dict):
                        parsed = ans
                    else:
                        parsed = None
                except Exception:
                    parsed = None

                if parsed and isinstance(parsed, dict):
                    q_text = parsed.get('question') or parsed.get('question_text')
                    options = parsed.get('options') or parsed.get('choices')
                    correct = parsed.get('correct')
                    explanation = parsed.get('explanation', '')

                    if q_text and options and len(options) >= 2 and (isinstance(correct, int) or (isinstance(correct, str) and correct.isdigit())):
                        # normalize correct to int
                        correct_idx = int(correct)
                        # ensure options length is at least 2; pad/truncate to 4
                        options = list(options)[:4] + ([''] * max(0, 4 - len(options)))

                        return {
                            'id': f'q_{question_num}',
                            'question_number': question_num,
                            'question_text': q_text,
                            'question_type': 'multiple_choice',
                            'options': options,
                            'correct_answer': correct_idx,
                            'correct_letter': chr(ord('A') + correct_idx) if 0 <= correct_idx < 26 else 'A',
                            'explanation': explanation or f'The correct answer is {chr(ord("A") + correct_idx)}',
                            'difficulty': difficulty,
                            'points': 1,
                            'user_answer': None,
                            'is_correct': None
                        }

            # Fallback to previous behavior if Gemini response invalid
            return self._generate_fallback_question(subject, difficulty, question_num)
                
        except Exception:
            return self._generate_fallback_question(subject, difficulty, question_num)
    
    def _parse_mcq_response(self, ai_response: str, question_num: int, difficulty: str) -> Dict:
        """Parse AI response into structured question format"""
        try:
            lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
            
            question_text = ""
            options = []
            correct_answer = ""
            explanation = ""
            
            import re
            for line in lines:
                if line.startswith('Question:') or line.startswith('• Question:'):
                    question_text = line.replace('Question:', '').replace('• Question:', '').strip()
                elif re.match(r'^[ABCD]\)|^•\s*[ABCD]\)', line):
                    # Strip leading bullets and letter prefixes like 'A) ' or '• A) '
                    option_text = re.sub(r'^•\s*', '', line).strip()
                    option_text = re.sub(r'^[ABCD]\)\s*', '', option_text).strip()
                    options.append(option_text)
                elif line.startswith('Correct Answer:') or line.startswith('• Correct Answer:'):
                    correct_answer = line.replace('Correct Answer:', '').replace('• Correct Answer:', '').strip()
                elif line.startswith('Explanation:') or line.startswith('• Explanation:'):
                    explanation = line.replace('Explanation:', '').replace('• Explanation:', '').strip()
            
            # Validate parsed data
            if not question_text or len(options) < 4:
                raise ValueError("Incomplete question data")
            
            # Extract correct answer letter
            correct_letter = correct_answer.upper().replace(')', '').strip()
            if correct_letter not in ['A', 'B', 'C', 'D']:
                correct_letter = 'A'  # Default fallback
            
            # Map letter to index
            correct_index = ord(correct_letter) - ord('A')
            
            return {
                'id': f'q_{question_num}',
                'question_number': question_num,
                'question_text': question_text,
                'question_type': 'multiple_choice',
                'options': options,
                'correct_answer': correct_index,
                'correct_letter': correct_letter,
                'explanation': explanation or f"The correct answer is {correct_letter}",
                'difficulty': difficulty,
                'points': 1,
                'user_answer': None,
                'is_correct': None
            }
            
        except Exception:
            return self._generate_fallback_question("General", difficulty, question_num)
    
    def _generate_true_false(self, subject: str, topic: str, difficulty: str, question_num: int) -> Dict:
        """Generate a true/false question"""
        try:
            context = f"Subject: {subject}"
            if topic:
                context += f", Topic: {topic}"
            
            prompt = f"""
            Generate a {difficulty} level true/false question for {subject}.
            {f"Focus on the topic: {topic}" if topic else ""}
            
            Format:
            Statement: [Your statement here]
            Answer: [True or False]
            Explanation: [Brief explanation]
            """
            
            response = self.qa_system.ask_question(prompt, context, provider="auto")
            
            if response['success']:
                return self._parse_true_false_response(response['answer'], question_num, difficulty)
            else:
                return self._generate_fallback_question(subject, difficulty, question_num)
                
        except Exception:
            return self._generate_fallback_question(subject, difficulty, question_num)
    
    def _parse_true_false_response(self, ai_response: str, question_num: int, difficulty: str) -> Dict:
        """Parse true/false response"""
        try:
            lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
            
            statement = ""
            answer = ""
            explanation = ""
            
            for line in lines:
                if line.startswith('Statement:') or line.startswith('• Statement:'):
                    statement = line.replace('Statement:', '').replace('• Statement:', '').strip()
                elif line.startswith('Answer:') or line.startswith('• Answer:'):
                    answer = line.replace('Answer:', '').replace('• Answer:', '').strip()
                elif line.startswith('Explanation:') or line.startswith('• Explanation:'):
                    explanation = line.replace('Explanation:', '').replace('• Explanation:', '').strip()
            
            if not statement:
                raise ValueError("No statement found")
            
            # Determine correct answer
            is_true = answer.lower().startswith('true')
            
            return {
                'id': f'q_{question_num}',
                'question_number': question_num,
                'question_text': statement,
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer': 0 if is_true else 1,
                'correct_letter': 'True' if is_true else 'False',
                'explanation': explanation or f"The statement is {answer.lower()}",
                'difficulty': difficulty,
                'points': 1,
                'user_answer': None,
                'is_correct': None
            }
            
        except Exception:
            return self._generate_fallback_question("General", difficulty, question_num)
    
    def _generate_fallback_question(self, subject: str, difficulty: str, question_num: int) -> Dict:
        """Generate fallback question when AI fails"""
        fallback_questions = {
            'easy': {
                'question': f'What is a fundamental concept in {subject}?',
                    'options': ['Basic principle', 'Advanced theory', 'Complex algorithm', 'Expert knowledge'],
                'correct': 0
            },
            'medium': {
                'question': f'Which approach is commonly used in {subject}?',
                    'options': ['Simple method', 'Standard approach', 'Complex procedure', 'Advanced technique'],
                'correct': 1
            },
            'hard': {
                'question': f'What is an advanced technique in {subject}?',
                    'options': ['Basic concept', 'Simple rule', 'Complex algorithm', 'Elementary principle'],
                'correct': 2
            }
        }
        
        template = fallback_questions.get(difficulty, fallback_questions['medium'])
        
        return {
            'id': f'q_{question_num}',
            'question_number': question_num,
            'question_text': template['question'],
            'question_type': 'multiple_choice',
            'options': template['options'],
            'correct_answer': template['correct'],
            'correct_letter': chr(ord('A') + template['correct']),
            'explanation': f'This is a {difficulty} level question about {subject}',
            'difficulty': difficulty,
            'points': 1,
            'user_answer': None,
            'is_correct': None
        }
    
    def _get_grading_scale(self) -> Dict:
        """Get grading scale for quiz scoring"""
        return {
            'A': {'min_percentage': 90, 'description': 'Excellent'},
            'B': {'min_percentage': 80, 'description': 'Good'},
            'C': {'min_percentage': 70, 'description': 'Satisfactory'},
            'D': {'min_percentage': 60, 'description': 'Needs Improvement'},
            'F': {'min_percentage': 0, 'description': 'Unsatisfactory'}
        }
    
    def _generate_instructions(self, difficulty: str) -> List[str]:
        """Generate quiz instructions based on difficulty"""
        base_instructions = [
            "Read each question carefully",
            "Select the best answer from the given options",
            "You can review and change your answers before submitting"
        ]
        
        difficulty_specific = {
            'easy': ["Take your time and think through each answer"],
            'medium': ["Consider multiple aspects of each question", "Some questions may have tricky wording"],
            'hard': ["Questions require deep understanding", "Consider edge cases and exceptions", "Multiple concepts may be combined in single questions"]
        }
        
        return base_instructions + difficulty_specific.get(difficulty, [])
    
    def submit_quiz(self, quiz_id: str, user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit quiz and calculate score
        
        Args:
            quiz_id (str): ID of the quiz
            user_answers (dict): User's answers {question_id: answer_index}
            
        Returns:
            dict: Quiz results with score and feedback
        """
        try:
            # In a real application, you would fetch the quiz from database
            # For now, return a mock result structure
            
            total_questions = len(user_answers)
            correct_answers = 0
            
            # Mock scoring (in real app, compare with correct answers)
            for question_id, user_answer in user_answers.items():
                # This is simplified - actual implementation would check against correct answers
                if random.random() > 0.3:  # 70% chance of being correct (mock)
                    correct_answers += 1
            
            score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Determine grade
            grade = 'F'
            grading_scale = self._get_grading_scale()
            for grade_letter, criteria in grading_scale.items():
                if score_percentage >= criteria['min_percentage']:
                    grade = grade_letter
                    break
            
            results = {
                'quiz_id': quiz_id,
                'submitted_at': datetime.now().isoformat(),
                'score': {
                    'correct_answers': correct_answers,
                    'total_questions': total_questions,
                    'percentage': round(score_percentage, 1),
                    'grade': grade,
                    'passed': score_percentage >= 60
                },
                'time_taken_minutes': random.randint(5, 20),  # Mock time
                'feedback': self._generate_feedback(score_percentage, grade),
                'detailed_results': user_answers  # In real app, include correct/incorrect for each question
            }
            
            return {
                'success': True,
                'results': results,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'results': None,
                'error': f'Error submitting quiz: {str(e)}'
            }
    
    def _generate_feedback(self, score_percentage: float, grade: str) -> str:
        """Generate personalized feedback based on performance"""
        if score_percentage >= 90:
            return "Excellent work! You have a strong understanding of the material."
        elif score_percentage >= 80:
            return "Good job! You understand most concepts well. Review the areas you missed."
        elif score_percentage >= 70:
            return "Satisfactory performance. Focus on strengthening your understanding of key concepts."
        elif score_percentage >= 60:
            return "You passed, but there's room for improvement. Consider reviewing the material again."
        else:
            return "You need to study more. Review the material and try again when ready."