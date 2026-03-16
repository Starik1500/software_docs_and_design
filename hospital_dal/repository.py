import csv
from sqlalchemy.orm import Session
from .interfaces import IDataRepository
from .models import Ward, Doctor, Patient, MedicalRecord

class DataRepository(IDataRepository):
    def __init__(self, session: Session):
        self.session = session

    def read_data_from_file(self, file_path: str) -> list[dict]:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def save_data_to_database(self, patients, wards, doctors):
        if self.session.query(Patient).first():
            return

        self.session.add_all(wards)
        self.session.add_all(doctors)
        self.session.add_all(patients)
        self.session.commit()
    
    def get_all_patients(self, page: int = 1, limit: int = 20):
        offset = (page - 1) * limit
        return self.session.query(Patient).offset(offset).limit(limit).all()

    def get_patient_by_id(self, patient_id: int):
        return self.session.query(Patient).filter(Patient.id == patient_id).first()

    def add_patient(self, patient: Patient):
        self.session.add(patient)
        self.session.commit()

    def update_patient(self, patient: Patient):
        self.session.commit()

    def delete_patient(self, patient_id: int):
        patient = self.get_patient_by_id(patient_id)
        if patient:
            self.session.delete(patient)
            self.session.commit()

    def get_all_doctors(self):
        return self.session.query(Doctor).all()

    def get_all_wards(self):
        return self.session.query(Ward).all()
    
    def get_free_wards(self):
        return self.session.query(Ward).filter(Ward.is_free == True).all()
    
    def clear_all_patients(self):
        self.session.query(MedicalRecord).delete()

        self.session.query(Patient).delete()

        self.session.query(Ward).update({Ward.is_free: True})
        
        self.session.commit()

    def count_patients_in_ward(self, ward_id: int) -> int:
        return self.session.query(Patient).filter(Patient.ward_id == ward_id).count()

    def update_ward_status(self, ward_id: int, is_free: bool):
        ward = self.session.query(Ward).filter(Ward.id == ward_id).first()
        if ward:
            ward.is_free = is_free
            self.session.commit()

    def get_available_doctors(self, current_doctor_id=None):
        all_doctors = self.session.query(Doctor).all()
        available_doctors = []
        
        for doc in all_doctors:
            count = self.session.query(Patient).filter(Patient.doctor_id == doc.id).count()

            if count < 5 or doc.id == current_doctor_id:
                available_doctors.append(doc)
                
        return available_doctors