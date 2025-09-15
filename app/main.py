from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql

# --- FastAPI app ---
app = FastAPI()

# --- Database connection (MySQL) ---
DATABASE_URL = "mysql+pymysql://root:Chinnari%4013@localhost/fastapi_app"
engine = create_engine(DATABASE_URL, echo=True)  # echo=True to see SQL logs
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy model ---
class User(Base):
    __tablename__ = "users"  # must match MySQL table name
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# --- Pydantic schema ---
class UserCreate(BaseModel):
    name: str
    email: str
    hashed_password: str

# --- POST endpoint ---
@app.post("/user/")
def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = User(
            name=user.name,
            email=user.email,
            hashed_password=user.hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "name": new_user.name, "email": new_user.email}
    finally:
        db.close()

# --- GET endpoint ---
@app.get("/")
def get_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()
