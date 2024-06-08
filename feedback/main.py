import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from feedback.models import Base
from feedback.schemas import FeedbackCreate, Feedback, FeedbackUpdate
from feedback.crud import create_feedback, get_feedback, update_feedback, delete_feedback, get_all_feedbacks
from typing import List 


load_dotenv()  

DATABASE_URL = os.getenv('DATABASE_URL') 

app = FastAPI(
    title="Feedback API",
    description="An API for collecting feedback scores",
    version="1.0.0"
)

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL environment variable set")

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()




@app.post("/feedback/", response_model=Feedback, summary="Submit Feedback", description="Submit a feedback score between 1 and 5.")
async def submit_feedback(feedback: FeedbackCreate, session: AsyncSession = Depends(get_session)):
    """
    Submit a feedback score.

    - **score**: An integer between 1 and 5 representing the feedback score.
    """
    return await create_feedback(feedback, session)

@app.get("/feedback/{feedback_id}", response_model=Feedback, summary="Get Feedback", description="Get a feedback by its ID.")
async def read_feedback(feedback_id: int, session: AsyncSession = Depends(get_session)):
    feedback = await get_feedback(feedback_id, session)
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@app.get("/feedbacks/", response_model=List[Feedback], summary="Get All Feedbacks", description="Get all feedbacks.")
async def read_feedbacks(session: AsyncSession = Depends(get_session)):
    return await get_all_feedbacks(session)

@app.put("/feedback/{feedback_id}", response_model=Feedback, summary="Update Feedback", description="Update a feedback by its ID.")
async def update_feedback_endpoint(feedback_id: int, feedback: FeedbackUpdate, session: AsyncSession = Depends(get_session)):
    updated_feedback = await update_feedback(feedback_id, feedback, session)
    if updated_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return updated_feedback

@app.delete("/feedback/{feedback_id}", summary="Delete Feedback", description="Delete a feedback by its ID.")
async def delete_feedback_endpoint(feedback_id: int, session: AsyncSession = Depends(get_session)):
    deleted = await delete_feedback(feedback_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"message": "Feedback deleted successfully"}