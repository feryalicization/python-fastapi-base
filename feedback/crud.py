from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from feedback.models import Feedback
from feedback.schemas import FeedbackCreate, FeedbackUpdate
from typing import List

async def create_feedback(feedback: FeedbackCreate, session: AsyncSession) -> Feedback:
    db_feedback = Feedback(score=feedback.score)
    session.add(db_feedback)
    await session.commit()
    await session.refresh(db_feedback)
    return db_feedback

async def get_feedback(feedback_id: int, session: AsyncSession) -> Feedback:
    result = await session.execute(select(Feedback).where(Feedback.id == feedback_id, Feedback.deleted_at.is_(None)))
    feedback = result.scalar_one_or_none()
    return feedback

async def get_all_feedbacks(session: AsyncSession) -> List[Feedback]:
    result = await session.execute(select(Feedback).where(Feedback.deleted_at.is_(None)))
    return result.scalars().all()

async def update_feedback(feedback_id: int, feedback_data: FeedbackUpdate, session: AsyncSession) -> Feedback:
    feedback = await get_feedback(feedback_id, session)
    if feedback is None:
        return None
    feedback.score = feedback_data.score
    await session.commit()
    await session.refresh(feedback)
    return feedback

async def delete_feedback(feedback_id: int, session: AsyncSession) -> bool:
    feedback = await get_feedback(feedback_id, session)
    if feedback is None:
        return False
    feedback.deleted_at = func.now()
    await session.commit()
    return True
