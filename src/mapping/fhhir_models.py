from pydantic import BaseModel, Field 
from typing import Optional, List

class Patient(BaseModel):
    resourceType: str = "Patient"
    id: str 
    gender: Optional[str] = None 
    birthDate: Optional[str] = None

class Condition(BaseModel):
    resourceType: str = "Condition"
    id: str 
    subject: dict
    code: dict
    
class MedicationRequest(BaseModel):
    resourceType: str = "MedicationRequest"
    id: str
    subject: dict
    medicationCodeableConcept: dict 
    dosage: Optional[list] = None

class BundleEntry(BaseModel):
    fullUrl: str
    resource: BaseModel

class Bundle(BaseModel):
    resourceType: str = "Bundle"
    type: str = "collection"
    entry: List[BundleEntry] = Field(default_factory=list)