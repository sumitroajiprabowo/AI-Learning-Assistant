"""
Q&A System Module - Milestone 2
Implements core Q&A functionality using Gemini/OpenAI APIs
Returns structured answers in bullet points
"""

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config import Config
import logging

logger = logging.getLogger(__name__)

class QASystem:
    """Q&A System using multiple AI providers"""
    
    def __init__(self):
        self.setup_apis()
        
    def setup_apis(self):
        """Initialize API connections"""
        try:
            if Config.OPENAI_API_KEY and openai is not None:
                openai.api_key = Config.OPENAI_API_KEY
                self.openai_available = True
            else:
                self.openai_available = False
                
            if Config.GEMINI_API_KEY and genai is not None:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)
                self.gemini_available = True
            else:
                self.gemini_available = False
                
        except Exception as e:
            logger.error(f"Error setting up APIs: {str(e)}")
            self.openai_available = False
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
    
    def ask_openai(self, question, context=""):
        """Ask question using OpenAI API"""
        if not self.openai_available or openai is None:
            return None
            
        try:
            prompt = f"""
            Please answer the following question in a structured bullet point format.
            Provide clear, concise bullet points that directly address the question.
            
            Context: {context}
            Question: {question}
            
            Answer in bullet points:
            """
            
            response = openai.ChatCompletion.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful learning assistant. Always provide answers in bullet point format using '•' symbols."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )
            
            answer = response.choices[0].message.content.strip()
            return self.format_answer_to_bullets(answer)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
    
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
            return None
    
    def ask_question(self, question, context="", provider="auto"):
        """
        Main method to ask questions
        
        Args:
            question (str): The question to ask
            context (str): Additional context for the question
            provider (str): "openai", "gemini", or "auto"
            
        Returns:
            dict: Response containing answer and metadata
        """
        if not question or not question.strip():
            return {
                "success": False,
                "error": "Question cannot be empty",
                "answer": None,
                "provider_used": None
            }
        
        answer = None
        provider_used = None
        
        if provider == "openai" or (provider == "auto" and self.openai_available):
            answer = self.ask_openai(question, context)
            if answer:
                provider_used = "openai"
        
        if not answer and (provider == "gemini" or (provider == "auto" and self.gemini_available)):
            answer = self.ask_gemini(question, context)
            if answer:
                provider_used = "gemini"
        
        if not answer:
            return {
                "success": False,
                "error": "No AI provider available or all providers failed",
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
        if self.openai_available:
            providers.append("openai")
        if self.gemini_available:
            providers.append("gemini")
        return providers
    
    def health_check(self):
        """Check health of QA system"""
        return {
            "openai_available": self.openai_available,
            "gemini_available": self.gemini_available,
            "total_providers": len(self.get_available_providers())
        }