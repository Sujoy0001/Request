import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.Students import Student
from app.schemas.Students import StudentCreate, StudentUpdate

logger = logging.getLogger(__name__)


def create_student(db: Session, student_data: StudentCreate) -> Student:
	student = Student(**student_data.model_dump())
	db.add(student)
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		logger.exception("Failed to create student")
		raise
	db.refresh(student)
	logger.info("Student created: student_id=%s", student.student_id)
	return student


def get_student(db: Session, student_id: UUID) -> Student | None:
	student = db.get(Student, student_id)
	logger.debug("Student lookup: student_id=%s found=%s", student_id, student is not None)
	return student


def get_students(
	db: Session, skip: int = 0, limit: int = 100, active_only: bool = False
) -> list[Student]:
	statement = select(Student)
	if active_only:
		statement = statement.where(Student.is_active.is_(True))
	statement = statement.offset(skip).limit(limit).order_by(Student.created_at.desc())
	students = list(db.scalars(statement).all())
	logger.info(
		"Students listed: count=%s skip=%s limit=%s active_only=%s",
		len(students), skip, limit, active_only,
	)
	return students


def update_student(
	db: Session, student: Student, student_data: StudentUpdate
) -> Student:
	for field, value in student_data.model_dump(exclude_unset=True).items():
		setattr(student, field, value)

	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		logger.exception("Failed to update student: student_id=%s", student.student_id)
		raise
	db.refresh(student)
	logger.info("Student updated: student_id=%s", student.student_id)
	return student


def delete_student(db: Session, student: Student) -> None:
	db.delete(student)
	db.commit()
	logger.info("Student deleted: student_id=%s", student.student_id)


def set_student_active(db: Session, student: Student, is_active: bool) -> Student:
	student.is_active = is_active
	db.commit()
	db.refresh(student)
	logger.info("Student active status changed: student_id=%s is_active=%s", student.student_id, is_active)
	return student