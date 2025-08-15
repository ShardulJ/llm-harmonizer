import uuid
from .fhhir_models import Bundle, BundleEntry, Patient, Condition, MedicationRequest
from .normalizer import condition_norm, drug_norm, frequency_norm

def to_fhir_bundle(parsed:dict) -> Bundle:
    patient_id = str(uuid.uuid4())
    patient = Patient(id=patient_id)

    if parsed.get("patient", {}).get("sex"):
        patient.gender = parsed["patient"]["sex"]

    entries = [BundleEntry(
        fullUrl=f"urn:uuid:{patient_id}",
        resource=patient.model_dump()
    )]

    for cond in parsed.get("conditions", []):
        coding = condition_norm(cond.get("name", "")) or {"system": "", "code": "", "display": cond.get("name", "")}
        cid = str(uuid.uuid4())
        condition = Condition(
            id=cid,
            subject={"reference": f"urn:uuid:{patient_id}"},
            code={
                "coding": [coding]
            }
        )
        entries.append(BundleEntry(
            fullUrl=f"urn:uuid:{cid}",
            resource=condition.model_dump()
        ))

    for med in parsed.get("med", []):
        coding = drug_norm(med.get("name", "")) or {"system": "", "code": "", "display": med.get("name", "")}
        mid = str(uuid.uuid4())
        dosage = []

        dose = med.get("dose")
        unit = med.get("unit")
        frequency = med.get("frequency")
        if dose and unit:
            dosage.append({
                dosage.append({"doseAndRate": 
                               [{"doseQuantity": 
                                 {"value": dose, 
                                  "unit": unit}
                                }]
                            })
            })
        if frequency:
            dosage.append({"text": frequency_norm(frequency)})
        medication = MedicationRequest(
            id=mid,
            subject={"reference": f"Patient/{patient_id}"},
            medicationCodeableConcept={
                "coding": [coding]
            },
            dosage=dosage if dosage else None
        )
        entries.append(BundleEntry(
            fullUrl=f"urn:uuid:{mid}",
            resource=medication.model_dump()
        ))
    return Bundle(entry=entries)