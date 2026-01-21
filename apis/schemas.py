from pydantic import BaseModel
from typing import Optional, List


class CityCreate(BaseModel):
    # document_id: str
    name: str
    state: Optional[str] = None
    country: str
    capital: Optional[bool] = False
    population: Optional[int] = 0
    regions: Optional[List[str]] = []


class CityUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    capital: Optional[bool] = None
    population: Optional[int] = None
    regions: Optional[List[str]] = None


class UpdateField(BaseModel):
    field: str
    value: object


class RegionUpdate(BaseModel):
    regions: List[str]


class IncrementValue(BaseModel):
    value: int


class DeleteField(BaseModel):
    field_name: str
