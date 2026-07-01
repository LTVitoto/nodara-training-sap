from pydantic import BaseModel, Field, field_validator

class SapBusinessPartnerPayload(BaseModel):
    Country: str = Field(..., min_length=2, max_length=2)
    BP_Role: str = Field(..., pattern=r"^FLCU\d{2}$")

    @field_validator('Country')
    @classmethod
    def country_must_be_uppercase(cls, v: str) -> str:
        if not v.isupper(): raise ValueError('País debe ser mayúsculas')
        return v

class SapEHSIncidentPayload(BaseModel):
    IncidentCategory: str = Field(..., min_length=2)
    Severity: str = Field(...)
    Description: str = Field(...)
    Plant: str = Field(..., min_length=4)
