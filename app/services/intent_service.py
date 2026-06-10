import logging

logger = logging.getLogger("ai_assistant")


class IntentService:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def _rule_based_intent(self, message: str) -> str:
        msg_lower = message.lower()
        if "vip" in msg_lower or "premium" in msg_lower or "وی آی پی" in msg_lower:
            return "vip_question"
        if (
            "exchange" in msg_lower
            or "register" in msg_lower
            or "sign up" in msg_lower
            or "صرافی" in msg_lower
            or "ثبت نام" in msg_lower
            or "ثبت‌نام" in msg_lower
        ):
            return "exchange_registration"
        if "kol" in msg_lower or "influencer" in msg_lower or "همکاری" in msg_lower:
            return "kol_collaboration"
        if (
            "support" in msg_lower
            or "problem" in msg_lower
            or "paid" in msg_lower
            or "subscription" in msg_lower
            or "مشکل" in msg_lower
            or "پرداخت" in msg_lower
            or "پشتیبانی" in msg_lower
        ):
            return "support_request"
        if (
            "service" in msg_lower
            or "what" in msg_lower
            or "how" in msg_lower
            or "چطور" in msg_lower
            or "چگونه" in msg_lower
            or "چیست" in msg_lower
        ):
            return "general_info"
        return "unknown"

    def _rule_based_segment(self, intent: str) -> str:
        mapping = {
            "vip_question": "vip_interest",
            "exchange_registration": "exchange_signup",
            "kol_collaboration": "kol_candidate",
            "support_request": "support_needed",
            "general_info": "general_question",
            "unknown": "new_user"
        }
        return mapping.get(intent, "new_user")

    def process(self, message: str):
        # 1. Rule-based check
        rule_intent = self._rule_based_intent(message)
        rule_segment = self._rule_based_segment(rule_intent)

        # 2. LLM check (if available)
        llm_intent = "unknown"
        llm_segment = "new_user"

        if self.llm_client.provider != "mock":
            try:
                llm_intent_raw = self.llm_client.detect_intent(message)
                valid_intents = ["vip_question", "exchange_registration",
                                 "kol_collaboration", "support_request", "general_info"]
                for v in valid_intents:
                    if v in llm_intent_raw:
                        llm_intent = v
                        break
                llm_segment = self._rule_based_segment(llm_intent)
            except Exception as e:
                logger.error(f"LLM intent detection failed: {e}")

        # 3. Decision logic: use LLM only when rules did not find a strong intent.
        final_intent = rule_intent
        final_segment = rule_segment

        if (
            self.llm_client.provider != "mock"
            and llm_intent != "unknown"
            and rule_intent in {"unknown", "general_info"}
        ):
            final_intent = llm_intent
            final_segment = llm_segment

        logger.info(
            f"Intent Check -> Rule: {rule_intent}, LLM: {llm_intent}, Final: {final_intent}")
        return final_intent, final_segment
