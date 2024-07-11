from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, Response, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import models
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
router_v1 = APIRouter(prefix='/api/v1')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils

@router_v1.get('/students')
async def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@router_v1.get('/students/{student_id}')
async def get_student(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

@router_v1.post('/students')
async def create_student(student: dict, response: Response, db: Session = Depends(get_db)):
    # TODO: Add validation
    newstudent = models.Student(firstname=student['firstname'], lastname=student['lastname'], stu_id=student['stu_id'], dob=student['dob'], sex=student['sex'], age=student['age'])
    db.add(newstudent)
    db.commit()
    db.refresh(newstudent)
    response.status_code = 201
    return newstudent

@router_v1.patch('/students/{student_id}')
async def update_student(student_id: int, student: dict, db: Session = Depends(get_db)):
    stu_info = db.query(models.Student).filter(models.Student.id == student_id).first()
    if stu_info == None:
        raise HTTPException(404, "Student Not found")
    stu_info.firstname = student.get("firstname", None)
    stu_info.lastname = student.get("lastname", None)
    stu_info.stu_id = student.get("stu_id", None)
    stu_info.dob = student.get("dob", None)
    stu_info.sex = student.get("sex", None)
    stu_info.age = student.get("age", None)
    db.commit()
    db.refresh(stu_info)
    return stu_info

@router_v1.delete('/students/{student_id}')
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    stu_info = db.query(models.Student).filter(models.Student.id == student_id).first()
    if stu_info == None:
        raise HTTPException(404, "Student Not found")
    db.delete(stu_info)
    db.commit()
    return {
        "message": "Student infomation is deleted"
    }

app.include_router(router_v1)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
