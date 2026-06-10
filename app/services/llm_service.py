import requests
import logging
from ..config import settings

logger = logging.getLogger("ai_assistant")


class LLMClient:
    def __init__(self):
        self.provider = self._determine_provider()
        logger.info(f"LLM Provider initialized: {self.provider}")

    def _determine_provider(self):
        if settings.LLM_PROVIDER != "auto":
            return settings.LLM_PROVIDER

        if settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY:
            return "api"
        if self._check_local_model():
            return "local"
        return "mock"

    def _check_local_model(self):
        try:
            res = requests.get("http://localhost:11434/api/tags", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def generate_reply(self, message: str, context: str = "") -> str:
        """Generate a proper reply using context from KB"""
        if not context or len(context.strip()) < 10:
            context = "No relevant information found in knowledge base."

        prompt = f"""Context from Knowledge Base:
{context}

User Question: {message}

دستور: بر اساس Context بالا، یک پاسخ طبیعی، مفید و به زبان فارسی بده.
اگر Context مرتبط نبود، پاسخ مودبانه و عمومی بده.
پاسخ را کوتاه و واضح نگه دار."""

        return self._call_llm(prompt)

    def detect_intent(self, message: str) -> str:
        """Detect intent"""
        prompt = f"""Classify the intent of this message into exactly one of these categories:
- vip_question
- exchange_registration
- kol_collaboration
- support_request
- general_info
- unknown

Message: {message}

Just return the intent name only."""

        intent = self._call_llm(prompt).strip().lower()
        # Fallback validation
        valid_intents = {"vip_question", "exchange_registration", "kol_collaboration",
                         "support_request", "general_info", "unknown"}
        if intent not in valid_intents:
            intent = "general_info"
        return intent

    def _call_llm(self, prompt: str) -> str:
        if self.provider == "api":
            return self._call_api(prompt)
        elif self.provider == "local":
            return self._call_local(prompt)
        else:
            return self._call_mock(prompt)

    def _call_api(self, prompt: str) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"API LLM Error: {e}")
            return self._call_mock(prompt)

    def _call_local(self, prompt: str) -> str:
        try:
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            return res.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Local LLM Error: {e}")
            return self._call_mock(prompt)

    def _call_mock(self, prompt: str) -> str:
        """Strong mock with context awareness"""
        if "Classify the intent" in prompt:
            msg = prompt.lower()
            if any(k in msg for k in ["vip", "وی آی پی", "خدمات vip"]):
                return "vip_question"
            if any(k in msg for k in ["صرافی", "ثبت‌نام", "register", "exchange"]):
                return "exchange_registration"
            if any(k in msg for k in ["kol", "KOL", "influencer", "همکاری"]):
                return "kol_collaboration"
            if any(k in msg for k in ["مشکل", "پرداخت", "support", "problem"]):
                return "support_request"
            return "general_info"

        # Reply generation from context
        if "Context from Knowledge Base" in prompt:
            try:
                context = prompt.split("Context from Knowledge Base:")[
                    1].split("User Question:")[0].strip()
                if len(context) > 30:
                    # Take first meaningful paragraph
                    reply = context[:600].strip()
                    if len(reply) > 50:
                        return reply + "\n\nبرای اطلاعات بیشتر خوشحال می‌شم کمک کنم!"
            except:
                pass

        return "سلام! بر اساس دانش داخلی راستاد، سؤال شما را بررسی کردم. لطفاً جزئیات بیشتری بفرمایید تا دقیق‌تر راهنمایی کنم."
