"""
Q&A System Module - Milestone 2
Implements core Q&A functionality using Gemini APIs
Returns structured answers in bullet points
"""

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config import Config
import logging
import json

logger = logging.getLogger(__name__)

class QASystem:
    """Q&A System using Gemini only"""
    
    def __init__(self):
        self.last_error = None
        self.setup_apis()
        
    def setup_apis(self):
        """Initialize API connections"""
        try:
            self.last_error = None
            if Config.GEMINI_API_KEY and genai is not None:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)
                self.gemini_available = True
            else:
                self.gemini_available = False
                
        except Exception as e:
            logger.error(f"Error setting up APIs: {str(e)}")
            self.last_error = str(e)
            self.gemini_available = False
    
    def format_answer_to_bullets(self, answer):
        """Convert answer to bullet point format"""
        if not answer:
            return "• No answer available"
            
        # If already in bullet format, return as is
        if answer.strip().startswith('•') or answer.strip().startswith('-'):
            return answer
            
        # Split answer into sentences and convert to bullets
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        if len(sentences) <= 1:
            return f"• {answer}"
            
        bullets = []
        for sentence in sentences:
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            bullets.append(f"• {sentence}")
            
        return '\n'.join(bullets)
    
    def ask_gemini(self, question, context=""):
        """Ask question using Gemini API"""
        if not self.gemini_available or genai is None:
            return None
            
        try:
            prompt = f"""
            Please answer the following question in a structured bullet point format.
            Use bullet points (•) to organize your response clearly.
            
            Context: {context}
            Question: {question}
            
            Provide a well-structured answer in bullet points:
            """
            
            response = self.gemini_model.generate_content(prompt)
            answer = response.text.strip()
            return self.format_answer_to_bullets(answer)
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            self.last_error = str(e)
            return None
    
    def ask_question(self, question, context="", provider="auto"):
        """
        Main method to ask questions
        
        Args:
            question (str): The question to ask
            context (str): Additional context for the question
            provider (str): "gemini" or "auto"
            
        Returns:
            dict: Response containing answer and metadata
        """
        if isinstance(question, dict):
            is_empty_question = not question or not question.get('instruction')
        else:
            is_empty_question = not question or not str(question).strip()

        if is_empty_question:
            return {
                "success": False,
                "error": "Question cannot be empty",
                "answer": None,
                "provider_used": None
            }
        
        answer = None
        provider_used = None

        if provider not in ("auto", "gemini"):
            return {
                "success": False,
                "error": "Only Gemini is supported",
                "answer": None,
                "provider_used": None
            }

        if self.gemini_available:
            # If question is a dict, assume caller requests raw/structured output
            if isinstance(question, dict):
                try:
                    instr = question.get('instruction') or json.dumps(question)
                    # call Gemini directly with instruction and return raw text
                    resp = self.gemini_model.generate_content(instr)
                    raw = (resp.text or "").strip()
                    provider_used = 'gemini'
                    return {
                        'success': True,
                        'error': None,
                        'answer': raw,
                        'provider_used': provider_used,
                        'question': question,
                        'context': context
                    }
                except Exception as e:
                    logger.error(f"Gemini JSON request error: {e}")
                    self.last_error = str(e)
                    answer = None
            else:
                answer = self.ask_gemini(question, context)
                if answer:
                    provider_used = "gemini"
        
        if not answer:
            error_message = self.last_error or "Gemini API unavailable or failed to generate answer"
            return {
                "success": False,
                "error": error_message,
                "answer": "• Unable to generate answer at this time\n• Please check API configurations\n• Try again later",
                "provider_used": None
            }
        
        return {
            "success": True,
            "error": None,
            "answer": answer,
            "provider_used": provider_used,
            "question": question,
            "context": context
        }
    
    def get_available_providers(self):
        """Return list of available AI providers"""
        providers = []
        if self.gemini_available:
            providers.append("gemini")
        return providers
    
    def health_check(self):
        """Check health of QA system"""
        return {
            "gemini_available": self.gemini_available,
            "total_providers": len(self.get_available_providers())
        }