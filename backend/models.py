# backend/models.py
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON

class Year(str, Enum):
    Freshman="Freshman"; Sophomore="Sophomore"; Junior="Junior"
    Senior="Senior"; Graduate="Graduate"; Other="Other"

class ProfileBase(SQLModel):
    name: str
    year: Year
    major: Optional[str] = None
    budget: int
    move_in: Optional[date] = None
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    cleanliness: int; noise: int; study_time: int; social: int; sleep: int

class Profile(ProfileBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class ProfileCreate(ProfileBase): ...
class ProfileRead(ProfileBase):
    id: UUID
    created_at: datetime

class MatchExplanation(SQLModel):
    positives: list[str]
    cautions: list[str]

class MatchResult(SQLModel):
    a_id: UUID
    b_id: UUID
    score: int
    explanation: MatchExplanation
