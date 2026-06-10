from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from ..database import get_db
from .. import models, schemas

router = APIRouter()
logger = logging.getLogger("ai_assistant")

DEFAULT_REPLY = "سلام! پیام شما را دریافت کردم. لطفا کمی جزئیات بیشتر بفرمایید تا دقیق‌تر راهنمایی کنم."
SUPPORT_REPLY = "متوجه شدم برای این موضوع به پشتیبانی نیاز دارید. لطفا جزئیات خطا، زمان رخداد و شماره پیگیری را ارسال کنید تا تیم پشتیبانی بررسی کند."
TECHNICAL_ERROR_REPLY = "سلام! در حال حاضر برای پاسخ‌گویی با مشکل فنی روبه‌رو هستم. لطفا با پشتیبانی تماس بگیرید."


@router.post("/message", response_model=schemas.MessageResponse)
def process_message(req: schemas.MessageRequest, request: Request, db: Session = Depends(get_db)):
    # Inject services from app state
    llm_client = request.app.state.llm_client
    intent_service = request.app.state.intent_service
    kb_service = request.app.state.kb_service

    receive_time = datetime.utcnow()

    # 1. Error Management: Empty fields
    if not req.message or not req.message.strip():
        logger.error(
            f"[{receive_time}] Empty message received for user_id: {req.user_id}")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not req.user_id or not req.user_id.strip():
        logger.error(
            f"[{receive_time}] Empty user_id received with message: {req.message}")
        raise HTTPException(status_code=400, detail="user_id cannot be empty")

    try:
        # 2. Intent & Segment (Dual Check)
        intent, segment = intent_service.process(req.message)
        needs_human = (intent == "support_request")

        # 3. Generate Reply
        if needs_human:
            reply = SUPPORT_REPLY
        else:
            kb_context = kb_service.search(req.message)
            if not kb_context:
                logger.warning(
                    f"[{receive_time}] No suitable answer found in KB for user_id: {req.user_id}")
                kb_context = "I couldn't find specific information about that. Would you like to connect with a human agent?"
                needs_human = True

            try:
                reply = llm_client.generate_reply(req.message, kb_context)
                if not reply or not reply.strip():
                    logger.warning(
                        f"[{receive_time}] Empty LLM reply for user_id: {req.user_id}; using fallback reply")
                    reply = DEFAULT_REPLY
                    needs_human = True
            except Exception as e:
                logger.error(
                    f"[{receive_time}] LLM/Mock error during reply generation for user_id: {req.user_id}: {e}")
                reply = TECHNICAL_ERROR_REPLY
                needs_human = True

        # 5. Database Operations
        user = db.query(models.User).filter(
            models.User.user_id == req.user_id).first()
        if not user:
            user = models.User(user_id=req.user_id,
                               name=req.name, segment=segment)
            db.add(user)
        else:
            user.name = req.name
            user.segment = segment
            user.last_seen_at = receive_time
        db.commit()

        msg = models.Message(
            user_id=req.user_id, user_message=req.message, assistant_reply=reply,
            intent=intent, segment=segment, needs_human_support=needs_human
        )
        db.add(msg)
        db.commit()

        # 6. Log success
        logger.info(
            f"[{receive_time}] user_id: {req.user_id} | intent: {intent} | segment: {segment} | message: {req.message[:50]}")

        return schemas.MessageResponse(reply=reply, intent=intent, user_segment=segment, needs_human_support=needs_human)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"[{receive_time}] Unhandled error processing message for user_id: {req.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
