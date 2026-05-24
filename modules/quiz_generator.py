"""
Quiz Generator Module - Milestone 4
Implements dynamic MCQ generation based on difficulty levels
Creates relevant and challenging questions
"""

import json
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import Config
from .qa_system import QASystem

class QuizGenerator:
    """Generate interactive quizzes with multiple choice questions"""

    def __init__(self):
        self.qa_system = QASystem()
        self.quiz_store: Dict[str, Dict[str, Any]] = {}
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

            # Generate questions: prefer single batched MCQ call (fast, reliable)
            questions: List[Dict[str, Any]] = []
            if question_types == ['multiple_choice'] or set(question_types) == {'multiple_choice'}:
                questions = self._generate_mcq_batch(subject, topic, difficulty, num_questions)

            # Fallback or mixed types: per-question generation
            if len(questions) < num_questions:
                start_idx = len(questions)
                for i in range(start_idx, num_questions):
                    q = self._generate_single_question(
                        subject, topic, difficulty, i + 1, question_types
                    )
                    if q:
                        questions.append(q)

            # Final safety: pad with fallbacks if anything missing
            while len(questions) < num_questions:
                questions.append(
                    self._generate_fallback_question(subject, difficulty, len(questions) + 1)
                )

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

            self.quiz_store[quiz_id] = quiz

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
        """Generate a single quiz question (MCQ only)."""
        try:
            return self._generate_mcq(subject, topic, difficulty, question_num)
        except Exception:
            return self._generate_fallback_question(subject, difficulty, question_num)
    
    @staticmethod
    def _extract_json(raw: str) -> Optional[Any]:
        """Extract a JSON object/array from a model response, tolerating markdown fences."""
        if not raw or not isinstance(raw, str):
            return None
        text = raw.strip()
        # Strip ```json ... ``` or ``` ... ``` fences
        fence = re.match(r'^```(?:json)?\s*(.*?)\s*```$', text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        try:
            return json.loads(text)
        except Exception:
            pass
        # Fallback: grab the first {...} or [...] block
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                return None
        return None

    def _normalize_mcq(self, item: Dict[str, Any], question_num: int, difficulty: str) -> Optional[Dict]:
        """Validate and normalize a parsed MCQ dict into the internal question schema."""
        if not isinstance(item, dict):
            return None
        q_text = item.get('question') or item.get('question_text')
        options = item.get('options') or item.get('choices')
        correct = item.get('correct')
        if correct is None:
            correct = item.get('correct_answer')
        explanation = item.get('explanation', '')

        if not q_text or not options or len(options) < 2:
            return None
        if isinstance(correct, bool):
            return None
        if isinstance(correct, str):
            c = correct.strip()
            if not c:
                return None
            if c.isdigit():
                correct_idx = int(c)
            elif c[0].upper() in 'ABCD':
                correct_idx = ord(c[0].upper()) - ord('A')
            else:
                return None
        elif isinstance(correct, (int, float)):
            correct_idx = int(correct)
        else:
            return None

        options = [str(o).strip() for o in list(options)[:4] if str(o).strip()]
        if len(options) < 2 or not (0 <= correct_idx < len(options)):
            return None

        return {
            'id': f'q_{question_num}',
            'question_number': question_num,
            'question_text': str(q_text),
            'question_type': 'multiple_choice',
            'options': options,
            'correct_answer': correct_idx,
            'correct_letter': chr(ord('A') + correct_idx),
            'explanation': explanation or f'The correct answer is {chr(ord("A") + correct_idx)}',
            'difficulty': difficulty,
            'points': 1,
            'user_answer': None,
            'is_correct': None
        }

    def _generate_mcq_batch(self, subject: str, topic: str, difficulty: str,
                            num_questions: int) -> List[Dict]:
        """Generate all MCQs in a single Gemini call returning a JSON array."""
        try:
            context = f"Subject: {subject}"
            if topic:
                context += f", Topic: {topic}"

            prompt = {
                "instruction": (
                    f"Generate exactly {num_questions} distinct {difficulty} multiple choice "
                    f"questions about {subject}."
                    + (f" Focus on the topic: {topic}." if topic else "")
                    + " Return ONLY a valid JSON array (no markdown, no commentary). "
                    "Each element must follow this exact schema: "
                    "{\"question\": \"...\", \"options\": [\"...\", \"...\", \"...\", \"...\"], "
                    "\"correct\": 0, \"explanation\": \"...\"}. "
                    "Each question must have exactly 4 options. "
                    "\"correct\" is the zero-based index of the correct option."
                )
            }

            response = self.qa_system.ask_question(prompt, context, provider="gemini")
            if not response.get('success'):
                return []

            parsed = self._extract_json(response.get('answer'))
            if isinstance(parsed, dict):
                parsed = parsed.get('questions') if isinstance(parsed.get('questions'), list) else [parsed]
            if not isinstance(parsed, list):
                return []

            questions: List[Dict] = []
            for item in parsed:
                normalized = self._normalize_mcq(item, len(questions) + 1, difficulty)
                if normalized:
                    questions.append(normalized)
                if len(questions) >= num_questions:
                    break

            return questions

        except Exception:
            return []

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
                parsed = self._extract_json(response.get('answer'))
                if isinstance(parsed, list) and parsed:
                    parsed = parsed[0]
                normalized = self._normalize_mcq(parsed, question_num, difficulty)
                if normalized:
                    return normalized

            # Fallback to template question if Gemini response invalid
            return self._generate_fallback_question(subject, difficulty, question_num)

        except Exception:
            return self._generate_fallback_question(subject, difficulty, question_num)
    
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
        Submit quiz and calculate the real score using the stored quiz.

        Args:
            quiz_id: ID of the quiz returned by generate_quiz.
            user_answers: Mapping of question identifier -> selected option index.
                Keys may be the question number ("1", 1) or the question id ("q_1").
                Values may be int index, letter ("A"), or option text.
        """
        try:
            quiz = self.quiz_store.get(quiz_id)
            if not quiz:
                return {
                    'success': False,
                    'results': None,
                    'error': 'Quiz not found. Generate a quiz first.'
                }

            def normalize_answer(value: Any, options: List[str]) -> Optional[int]:
                if value is None:
                    return None
                if isinstance(value, bool):
                    return int(value)
                if isinstance(value, int):
                    return value if 0 <= value < len(options) else None
                if isinstance(value, str):
                    stripped = value.strip()
                    if stripped.isdigit():
                        idx = int(stripped)
                        return idx if 0 <= idx < len(options) else None
                    letter = stripped[:1].upper()
                    if letter and 'A' <= letter <= chr(ord('A') + len(options) - 1):
                        return ord(letter) - ord('A')
                    for i, opt in enumerate(options):
                        if str(opt).strip().lower() == stripped.lower():
                            return i
                return None

            questions = quiz.get('questions', [])
            total_questions = len(questions)
            correct_answers = 0
            detailed_results: Dict[str, Any] = {}

            for q in questions:
                qnum = q['question_number']
                options = q.get('options', [])
                lookup_keys = [str(qnum), qnum, q.get('id')]
                raw = None
                for key in lookup_keys:
                    if key is not None and key in user_answers:
                        raw = user_answers[key]
                        break

                user_idx = normalize_answer(raw, options)
                correct_idx = q.get('correct_answer')
                is_correct = user_idx is not None and user_idx == correct_idx
                if is_correct:
                    correct_answers += 1

                detailed_results[str(qnum)] = {
                    'question_text': q.get('question_text'),
                    'selected': user_idx,
                    'correct': correct_idx,
                    'is_correct': is_correct,
                    'selected_text': options[user_idx] if isinstance(user_idx, int) and 0 <= user_idx < len(options) else None,
                    'correct_text': options[correct_idx] if isinstance(correct_idx, int) and 0 <= correct_idx < len(options) else None,
                    'explanation': q.get('explanation', '')
                }

            score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            grade = 'F'
            for grade_letter, criteria in self._get_grading_scale().items():
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
                'feedback': self._generate_feedback(score_percentage, grade),
                'detailed_results': detailed_results
            }

            quiz['completed'] = True
            quiz['results'] = results

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