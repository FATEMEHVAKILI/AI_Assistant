import requests
import logging
from ..config import settings

logger = logging.getLogger("ai_assistant")


class LLMClient:
    def __init__(self):
        self.provider = self._determine_provider()
        logger.info(f"LLM Provider initialized: {self.provider}")

    def _determine_provider(self):
        # 1. Check if forced via .env
        if settings.LLM_PROVIDER != "auto":
            return settings.LLM_PROVIDER

        # 2. Priority 1: API
        if settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY:
            return "api"
        # 3. Priority 2: Local Model
        if self._check_local_model():
            return "local"
        # 4. Priority 3: Mock
        return "mock"

    def _check_local_model(self):
        try:
            res = requests.get("http://localhost:11434/api/tags", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def generate_reply(self, message: str, context: str) -> str:
        prompt = f"Context:\n{context}\n\nUser Question: {message}\n\nAnswer concisely based on the context."
        return self._call_llm(prompt)

    def detect_intent(self, message: str) -> str:
        prompt = f"Classify the intent of this message into exactly one of these: vip_question, exchange_registration, kol_collaboration, support_request, general_info, unknown.\nMessage: {message}\nIntent:"
        return self._call_llm(prompt).strip().lower()

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
                model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"API LLM Error: {e}")
            return self._call_mock(prompt)  # Fallback to mock on error

    def _call_local(self, prompt: str) -> str:
        try:
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3", "prompt": prompt, "stream": False
            }, timeout=30)
            return res.json().get("response", "")
        except Exception as e:
            logger.error(f"Local LLM Error: {e}")
            return self._call_mock(prompt)

    def _call_mock(self, prompt: str) -> str:
        if "Classify the intent" in prompt:
            msg = prompt.split("Message:")[-1].strip().lower()
            if "vip" in msg or "وی آی پی" in msg:
                return "vip_question"
            if "exchange" in msg or "register" in msg or "ثبت" in msg or "صرافی" in msg:
                return "exchange_registration"
            if "kol" in msg or "KOL" in msg or "influencer" in msg:
                return "kol_collaboration"
            if "support" in msg or "problem" in msg or "پرداخت" in msg or "مشکل" in msg:
                return "support_request"
            return "general_info"

        if "Context:" in prompt and "User Question:" in prompt:
            try:
                context = prompt.split("Context:")[1].split(
                    "User Question:")[0].strip()
                question = prompt.split("User Question:")[1].strip()

                if len(context) > 50:
                    sentences = context.split(
                        '۔')[:2] or context.split('.')[:2]
                    reply = " ".join(sentences).strip()
                    return reply + "\n\nبرای اطلاعات بیشتر خوشحال می‌شم کمک کنم!"
            except:
                pass

        return "بر اساس اطلاعات داخلی راستاد، این موضوع رو بررسی کردم. لطفاً جزئیات بیشتری بگید تا دقیق‌تر راهنمایی کنم."
