"""
Q&A System Module - Milestone 2
Implements core Q&A using Gemini (primary) with OpenAI fallback.
Returns structured answers in bullet points.
"""

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from config import Config
import logging
import json

logger = logging.getLogger(__name__)


class QASystem:
    """Q&A System with Gemini primary and OpenAI fallback."""

    def __init__(self):
        self.last_error = None
        self.gemini_available = False
        self.openai_available = False
        self.gemini_model = None
        self.openai_client = None
        self.setup_apis()

    def setup_apis(self):
        """Initialize Gemini and OpenAI clients if keys + SDKs present."""
        self.last_error = None
        try:
            if Config.GEMINI_API_KEY and genai is not None:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)
                self.gemini_available = True
        except Exception as e:
            logger.error(f"Gemini setup failed: {e}")
            self.last_error = str(e)
            self.gemini_available = False

        try:
            if Config.OPENAI_API_KEY and OpenAI is not None:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                self.openai_available = True
        except Exception as e:
            logger.error(f"OpenAI setup failed: {e}")
            self.last_error = str(e)
            self.openai_available = False

    def format_answer_to_bullets(self, answer):
        """Convert answer to bullet point format."""
        if not answer:
            return "• No answer available"
        if answer.strip().startswith('•') or answer.strip().startswith('-'):
            return answer
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        if len(sentences) <= 1:
            return f"• {answer}"
        bullets = []
        for sentence in sentences:
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            bullets.append(f"• {sentence}")
        return '\n'.join(bullets)

    # ----- Provider calls -----

    def _gemini_raw(self, instruction: str):
        if not self.gemini_available or self.gemini_model is None:
            return None
        try:
            resp = self.gemini_model.generate_content(instruction)
            return (resp.text or "").strip()
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            self.last_error = str(e)
            return None

    def _openai_raw(self, instruction: str):
        if not self.openai_available or self.openai_client is None:
            return None
        try:
            resp = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": instruction}],
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            self.last_error = str(e)
            return None

    def ask_gemini(self, question, context=""):
        """Bullet-formatted Gemini answer."""
        prompt = f"""
            Please answer the following question in a structured bullet point format.
            Use bullet points (•) to organize your response clearly.

            Context: {context}
            Question: {question}

            Provide a well-structured answer in bullet points:
            """
        raw = self._gemini_raw(prompt)
        return self.format_answer_to_bullets(raw) if raw else None

    def ask_openai(self, question, context=""):
        """Bullet-formatted OpenAI answer."""
        prompt = f"""
            Please answer the following question in a structured bullet point format.
            Use bullet points (•) to organize your response clearly.

            Context: {context}
            Question: {question}

            Provide a well-structured answer in bullet points:
            """
        raw = self._openai_raw(prompt)
        return self.format_answer_to_bullets(raw) if raw else None

    # ----- Public API -----

    def ask_question(self, question, context="", provider="auto"):
        """
        Main entry point.

        Args:
            question: str | dict. If dict with 'instruction', raw mode (no bullet formatting).
            context: str.
            provider: 'auto' (Gemini->OpenAI), 'gemini', or 'openai'.
        """
        if isinstance(question, dict):
            is_empty = not question or not question.get('instruction')
        else:
            is_empty = not question or not str(question).strip()
        if is_empty:
            return {
                "success": False,
                "error": "Question cannot be empty",
                "answer": None,
                "provider_used": None,
            }

        if provider not in ("auto", "gemini", "openai"):
            return {
                "success": False,
                "error": "Provider must be one of: auto, gemini, openai",
                "answer": None,
                "provider_used": None,
            }

        # Build ordered provider list
        if provider == "gemini":
            order = ["gemini"]
        elif provider == "openai":
            order = ["openai"]
        else:
            order = ["gemini", "openai"]

        raw_mode = isinstance(question, dict)
        instruction = (
            question.get('instruction') or json.dumps(question)
        ) if raw_mode else None

        answer = None
        provider_used = None

        for prov in order:
            if prov == "gemini" and self.gemini_available:
                if raw_mode:
                    answer = self._gemini_raw(instruction)
                else:
                    answer = self.ask_gemini(question, context)
                if answer:
                    provider_used = "gemini"
                    break
            elif prov == "openai" and self.openai_available:
                if raw_mode:
                    answer = self._openai_raw(instruction)
                else:
                    answer = self.ask_openai(question, context)
                if answer:
                    provider_used = "openai"
                    break

        if not answer:
            error_message = self.last_error or "No AI provider available"
            return {
                "success": False,
                "error": error_message,
                "answer": "• Unable to generate answer at this time\n• Please check API configurations\n• Try again later",
                "provider_used": None,
            }

        return {
            "success": True,
            "error": None,
            "answer": answer,
            "provider_used": provider_used,
            "question": question,
            "context": context,
        }

    def get_available_providers(self):
        providers = []
        if self.gemini_available:
            providers.append("gemini")
        if self.openai_available:
            providers.append("openai")
        return providers

    def health_check(self):
        return {
            "gemini_available": self.gemini_available,
            "openai_available": self.openai_available,
            "total_providers": len(self.get_available_providers()),
        }
