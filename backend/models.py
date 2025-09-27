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

# Apartment Models
class ApartmentComplex(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    phone_number: Optional[str] = None
    notes: Optional[str] = None
    lease_term: Optional[int] = None  # months
    lease_type: Optional[str] = None  # Individual/Joint
    studio_cost: Optional[str] = None
    one_bedroom_cost: Optional[str] = None
    two_bedroom_cost: Optional[str] = None
    three_bedroom_cost: Optional[str] = None
    four_bedroom_cost: Optional[str] = None
    five_bedroom_cost: Optional[str] = None
    application_fee: Optional[int] = None
    security_deposit: Optional[str] = None
    pets_allowed: Optional[bool] = None
    parking_included: Optional[bool] = None
    furniture_included: Optional[bool] = None
    utilities_included: Optional[str] = None  # JSON string of utilities
    laundry: Optional[str] = None
    additional_fees: Optional[str] = None
    distance_to_burruss: Optional[float] = None  # miles
    bus_stop_nearby: Optional[bool] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class ApartmentComplexCreate(SQLModel):
    name: str
    phone_number: Optional[str] = None
    notes: Optional[str] = None
    lease_term: Optional[int] = None
    lease_type: Optional[str] = None
    studio_cost: Optional[str] = None
    one_bedroom_cost: Optional[str] = None
    two_bedroom_cost: Optional[str] = None
    three_bedroom_cost: Optional[str] = None
    four_bedroom_cost: Optional[str] = None
    five_bedroom_cost: Optional[str] = None
    application_fee: Optional[int] = None
    security_deposit: Optional[str] = None
    pets_allowed: Optional[bool] = None
    parking_included: Optional[bool] = None
    furniture_included: Optional[bool] = None
    utilities_included: Optional[str] = None
    laundry: Optional[str] = None
    additional_fees: Optional[str] = None
    distance_to_burruss: Optional[float] = None
    bus_stop_nearby: Optional[bool] = None
    address: Optional[str] = None

class ApartmentComplexRead(ApartmentComplexCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
