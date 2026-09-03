from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.Students import BloodGroup, Gender


class StudentBase(BaseModel):
    student_name: str = Field(min_length=1, max_length=150)
    date_of_birth: date
    gender: Gender
    blood_group: BloodGroup | None = None
    photo_url: str | None = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_name: str | None = Field(default=None, min_length=1, max_length=150)
    date_of_birth: date | None = None
    gender: Gender | None = None
    blood_group: BloodGroup | None = None
    photo_url: str | None = None
    is_active: bool | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    student_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


Students = StudentRead