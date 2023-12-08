from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth,categories,questions,quizzes,results
from app.database.config import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware
origins = [
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(quizzes.router, prefix="/api/v1/quizzes", tags=["quizzes"])
app.include_router(results.router, prefix="/api/v1/results", tags=["results"])
