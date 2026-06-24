from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChemicalBase(BaseModel):
    cas_number: str
    name: str
    formula: str | None = None
    ghs_classification: str | None = None
    toxicity_score: float | None = None


class ChemicalResponse(ChemicalBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationCreate(BaseModel):
    input_text: str


class EvaluationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    input_text: str
    extracted_chemicals: list[str]
    overall_risk_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LLMLogResponse(BaseModel):
    id: uuid.UUID
    evaluation_id: uuid.UUID
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float

    model_config = ConfigDict(from_attributes=True)
