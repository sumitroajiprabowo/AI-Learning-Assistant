"""
Study Plan Generator Module - Milestone 3
Develops personalized study plans based on user goals, timelines, and subjects
Generates day-wise learning roadmaps
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
from config import Config
from .qa_system import QASystem

class StudyPlanGenerator:
    """Generate personalized study plans"""
    
    def __init__(self):
        self.qa_system = QASystem()
    
    def generate_study_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized study plan
        
        Args:
            user_input (dict): {
                'goals': str - Learning objectives
                'subjects': List[str] - Subjects to study
                'timeline': int - Duration in days
                'daily_hours': int - Hours per day
                'difficulty_level': str - 'beginner', 'intermediate', 'advanced'
                'learning_style': str - 'visual', 'auditory', 'kinesthetic', 'reading'
            }
            
        Returns:
            dict: Complete study plan with day-wise breakdown
        """
        try:
            # Validate input
            validation_result = self._validate_input(user_input)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'plan': None
                }
            
            # Extract parameters
            goals = user_input.get('goals', '')
            subjects = user_input.get('subjects', [])
            timeline = user_input.get('timeline', Config.DEFAULT_STUDY_DURATION)
            daily_hours = user_input.get('daily_hours', Config.DEFAULT_DAILY_HOURS)
            difficulty = user_input.get('difficulty_level', 'intermediate')
            learning_style = user_input.get('learning_style', 'mixed')
            
            # Generate plan structure
            plan_id = str(uuid.uuid4())
            created_date = datetime.now().isoformat()
            
            # Generate daily breakdown
            daily_plan = self._generate_daily_breakdown(
                subjects, timeline, daily_hours, difficulty, learning_style, goals
            )
            
            # Generate study resources
            resources = self._generate_study_resources(subjects, difficulty)
            
            # Generate milestones
            milestones = self._generate_milestones(timeline, subjects)
            
            study_plan = {
                'success': True,
                'plan': {
                    'id': plan_id,
                    'created_date': created_date,
                    'metadata': {
                        'goals': goals,
                        'subjects': subjects,
                        'timeline_days': timeline,
                        'daily_hours': daily_hours,
                        'difficulty_level': difficulty,
                        'learning_style': learning_style,
                        'total_study_hours': timeline * daily_hours
                    },
                    'daily_breakdown': daily_plan,
                    'milestones': milestones,
                    'recommended_resources': resources,
                    'progress_tracking': {
                        'completed_days': 0,
                        'total_days': timeline,
                        'completion_percentage': 0,
                        'last_updated': created_date
                    }
                }
            }
            
            return study_plan
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating study plan: {str(e)}',
                'plan': None
            }
    
    def _validate_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user input for study plan generation"""
        if not isinstance(user_input, dict):
            return {'valid': False, 'error': 'Input must be a dictionary'}
        
        required_fields = ['subjects']
        for field in required_fields:
            if field not in user_input or not user_input[field]:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        # Validate subjects
        subjects = user_input.get('subjects', [])
        if not isinstance(subjects, list) or len(subjects) == 0:
            return {'valid': False, 'error': 'Subjects must be a non-empty list'}
        
        # Validate timeline
        timeline = user_input.get('timeline', Config.DEFAULT_STUDY_DURATION)
        if not isinstance(timeline, int) or timeline <= 0 or timeline > 365:
            return {'valid': False, 'error': 'Timeline must be between 1 and 365 days'}
        
        # Validate daily hours
        daily_hours = user_input.get('daily_hours', Config.DEFAULT_DAILY_HOURS)
        if not isinstance(daily_hours, (int, float)) or daily_hours <= 0 or daily_hours > 16:
            return {'valid': False, 'error': 'Daily hours must be between 0.5 and 16'}
        
        return {'valid': True, 'error': None}
    
    def _generate_daily_breakdown(self, subjects: List[str], timeline: int, 
                                daily_hours: int, difficulty: str, 
                                learning_style: str, goals: str) -> List[Dict]:
        """Generate day-by-day study breakdown"""
        daily_plan = []
        subjects_cycle = subjects * ((timeline // len(subjects)) + 1)
        
        for day in range(1, timeline + 1):
            date = (datetime.now() + timedelta(days=day-1)).strftime('%Y-%m-%d')
            
            # Determine primary subject for the day
            primary_subject = subjects_cycle[day - 1]
            
            # Generate daily topics using AI
            daily_topics = self._generate_daily_topics(
                primary_subject, day, timeline, difficulty, goals
            )
            
            # Distribute hours across activities
            activities = self._distribute_daily_activities(
                primary_subject, daily_hours, learning_style, daily_topics
            )
            
            daily_plan.append({
                'day': day,
                'date': date,
                'primary_subject': primary_subject,
                'total_hours': daily_hours,
                'topics': daily_topics,
                'activities': activities,
                'completed': False,
                'notes': ''
            })
        
        return daily_plan
    
    def _generate_daily_topics(self, subject: str, day: int, total_days: int, 
                             difficulty: str, goals: str) -> List[str]:
        """Generate topics for a specific day using AI"""
        try:
            # Calculate progress percentage
            progress = (day - 1) / total_days * 100
            
            prompt = f"""
            Generate 3-5 specific learning topics for day {day} of a {total_days}-day study plan.
            Subject: {subject}
            Difficulty: {difficulty}
            Progress: {progress:.0f}% through the course
            Learning goals: {goals}
            
            Provide topics that are appropriate for this stage of learning.
            """
            
            response = self.qa_system.ask_question(prompt, provider="auto")
            if response['success']:
                # Extract topics from bullet points
                topics = []
                for line in response['answer'].split('\n'):
                    if line.strip().startswith('•'):
                        topic = line.strip()[1:].strip()
                        if topic:
                            topics.append(topic)
                return topics[:5]  # Limit to 5 topics
            
            # Fallback topics if AI fails
            return self._get_fallback_topics(subject, day, difficulty)
            
        except Exception:
            return self._get_fallback_topics(subject, day, difficulty)
    
    def _get_fallback_topics(self, subject: str, day: int, difficulty: str) -> List[str]:
        """Fallback topics when AI is not available"""
        fallback_topics = {
            'python': [
                'Variables and Data Types',
                'Control Structures',
                'Functions and Modules',
                'Object-Oriented Programming',
                'File Handling'
            ],
            'mathematics': [
                'Basic Arithmetic',
                'Algebra Fundamentals',
                'Geometry Concepts',
                'Statistics Basics',
                'Calculus Introduction'
            ],
            'data science': [
                'Data Manipulation',
                'Statistical Analysis',
                'Data Visualization',
                'Machine Learning Basics',
                'Data Cleaning'
            ]
        }
        
        # Get topics for subject or use generic ones
        topics = fallback_topics.get(subject.lower(), [
            f'{subject} Fundamentals',
            f'{subject} Core Concepts',
            f'{subject} Practical Applications',
            f'{subject} Advanced Topics',
            f'{subject} Review and Practice'
        ])
        
        # Return topics based on day (cycle through)
        start_idx = ((day - 1) % len(topics))
        return topics[start_idx:start_idx + 3]
    
    def _distribute_daily_activities(self, subject: str, daily_hours: int, 
                                   learning_style: str, topics: List[str]) -> List[Dict]:
        """Distribute daily hours across different learning activities"""
        activities = []
        
        # Activity types based on learning style
        activity_templates = {
            'visual': [
                {'type': 'Video Learning', 'percentage': 0.4},
                {'type': 'Diagram Study', 'percentage': 0.3},
                {'type': 'Practice Problems', 'percentage': 0.3}
            ],
            'auditory': [
                {'type': 'Audio Lectures', 'percentage': 0.4},
                {'type': 'Discussion/Teaching', 'percentage': 0.3},
                {'type': 'Practice Problems', 'percentage': 0.3}
            ],
            'kinesthetic': [
                {'type': 'Hands-on Practice', 'percentage': 0.5},
                {'type': 'Project Work', 'percentage': 0.3},
                {'type': 'Theory Review', 'percentage': 0.2}
            ],
            'reading': [
                {'type': 'Reading Materials', 'percentage': 0.4},
                {'type': 'Note Taking', 'percentage': 0.3},
                {'type': 'Practice Problems', 'percentage': 0.3}
            ]
        }
        
        # Get activity template or use mixed approach
        template = activity_templates.get(learning_style, activity_templates['visual'])
        
        for i, activity_info in enumerate(template):
            duration = round(daily_hours * activity_info['percentage'], 1)
            if duration > 0:
                activities.append({
                    'activity': activity_info['type'],
                    'duration_hours': duration,
                    'topics_covered': topics[:2] if i == 0 else topics[2:],
                    'completed': False
                })
        
        return activities
    
    def _generate_milestones(self, timeline: int, subjects: List[str]) -> List[Dict]:
        """Generate milestone checkpoints for the study plan"""
        milestones = []
        
        # Calculate milestone intervals
        milestone_interval = max(7, timeline // 4)  # Weekly or quarterly milestones
        
        for i in range(milestone_interval, timeline + 1, milestone_interval):
            if i <= timeline:
                milestone = {
                    'day': i,
                    'title': f'Milestone {len(milestones) + 1}: Progress Check',
                    'description': f'Review progress in {", ".join(subjects)}',
                    'tasks': [
                        'Complete self-assessment quiz',
                        'Review challenging topics',
                        'Update study strategy if needed'
                    ],
                    'completed': False
                }
                milestones.append(milestone)
        
        return milestones
    
    def _generate_study_resources(self, subjects: List[str], difficulty: str) -> Dict:
        """Generate recommended study resources"""
        return {
            'books': [f'{subject.title()} - {difficulty.title()} Guide' for subject in subjects],
            'online_courses': [f'Online {subject} Course ({difficulty})' for subject in subjects],
            'practice_platforms': [
                'LeetCode (for programming)',
                'Khan Academy (for mathematics)',
                'Coursera (for comprehensive courses)',
                'edX (for university-level content)'
            ],
            'tools': [
                'Jupyter Notebook (for data science)',
                'VS Code (for programming)',
                'Notion (for note-taking)',
                'Anki (for memorization)'
            ]
        }
    
    def update_progress(self, plan_id: str, day: int, completed: bool, notes: str = "") -> Dict:
        """Update progress for a specific day"""
        # This would typically update a database
        # For now, return success response
        return {
            'success': True,
            'message': f'Progress updated for day {day}',
            'plan_id': plan_id
        }
    
    def get_plan_summary(self, plan: Dict) -> Dict:
        """Get summary of a study plan"""
        if not plan or 'plan' not in plan:
            return {'error': 'Invalid plan'}
        
        plan_data = plan['plan']
        metadata = plan_data.get('metadata', {})
        daily_breakdown = plan_data.get('daily_breakdown', [])
        
        completed_days = sum(1 for day in daily_breakdown if day.get('completed', False))
        total_days = len(daily_breakdown)
        completion_percentage = (completed_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'plan_id': plan_data.get('id'),
            'subjects': metadata.get('subjects', []),
            'timeline_days': metadata.get('timeline_days', 0),
            'daily_hours': metadata.get('daily_hours', 0),
            'total_study_hours': metadata.get('total_study_hours', 0),
            'completed_days': completed_days,
            'completion_percentage': round(completion_percentage, 1),
            'remaining_days': total_days - completed_days
        }