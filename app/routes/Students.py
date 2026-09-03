import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.Students import (
    create_student,
    delete_student,
    get_student,
    get_students,
    set_student_active,
    update_student,
)
from app.db.neon import get_db
from app.schemas.Students import StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])
logger = logging.getLogger(__name__)


@router.post("", response_model=StudentRead, status_code=201)
def create_student_route(student_data: StudentCreate, db: Session = Depends(get_db)):
    try:
        return create_student(db, student_data)
    except IntegrityError as error:
        logger.warning("Student creation conflict")
        raise HTTPException(status_code=409, detail="Student could not be created") from error


@router.get("", response_model=list[StudentRead])
def list_students_route(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    if skip < 0 or limit < 1 or limit > 100:
        logger.warning("Invalid student pagination: skip=%s limit=%s", skip, limit)
        raise HTTPException(status_code=400, detail="Invalid pagination values")
    return get_students(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/{student_id}", response_model=StudentRead)
def get_student_route(student_id: UUID, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if student is None:
        logger.info("Student not found: student_id=%s", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=StudentRead)
def update_student_route(
    student_id: UUID,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
):
    student = get_student(db, student_id)
    if student is None:
        logger.info("Student not found for update: student_id=%s", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        return update_student(db, student, student_data)
    except IntegrityError as error:
        logger.warning("Student update conflict: student_id=%s", student_id)
        raise HTTPException(status_code=409, detail="Student could not be updated") from error


@router.delete("/{student_id}", status_code=204)
def delete_student_route(student_id: UUID, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if student is None:
        logger.info("Student not found for deletion: student_id=%s", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    delete_student(db, student)


@router.patch("/{student_id}/activate", response_model=StudentRead)
def activate_student_route(student_id: UUID, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if student is None:
        logger.info("Student not found for activation: student_id=%s", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    return set_student_active(db, student, True)


@router.patch("/{student_id}/deactivate", response_model=StudentRead)
def deactivate_student_route(student_id: UUID, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if student is None:
        logger.info("Student not found for deactivation: student_id=%s", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    return set_student_active(db, student, False)