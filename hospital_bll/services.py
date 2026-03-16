from datetime import datetime
from hospital_dal.interfaces import IDataRepository
from hospital_dal.models import Ward, Doctor, Patient, MedicalRecord
from .interfaces import IHospitalService

class HospitalService(IHospitalService):
    def __init__(self, data_repository: IDataRepository):
        self._data_repo = data_repository

    def process_and_save_data(self, csv_file_path: str):
        raw_data = self._data_repo.read_data_from_file(csv_file_path)
        
        self._data_repo.session.query(MedicalRecord).delete()
        self.clear_all_patients()
        self._data_repo.session.query(Doctor).delete()
        self._data_repo.session.query(Ward).delete()
        self._data_repo.session.commit()

        wards_dict = {}
        for w_num in [101, 102, 103, 104, 201, 202, 203, 301, 305]:
            ward = Ward(ward_number=w_num, floor=w_num // 100, is_free=True)
            self._data_repo.session.add(ward)
            wards_dict[str(w_num)] = ward
            
        doctors_dict = {}
        for d_name in ["Dr. Старик", "Dr. Батіг", "Dr. Грибовський", "Dr. Кравченко", "Dr. Грабар", "Dr. Шевченко", "Dr. Мельник", "Dr. Мороз", "Dr. Сатана", "Dr. Савченко"]:
            doc = Doctor(name=d_name, specialization="Загальна практика")
            self._data_repo.session.add(doc)
            doctors_dict[d_name] = doc
            
        self._data_repo.session.commit()

        for row in raw_data:
            w_num = row['WardNumber']
            d_name = row['DoctorName']
            
            ward_id = wards_dict[w_num].id if w_num in wards_dict else None
            doctor_id = doctors_dict[d_name].id if d_name in doctors_dict else None

            if ward_id and self._data_repo.count_patients_in_ward(ward_id) >= 4:
                ward_id = None
                
            if doctor_id:
                count_doc = self._data_repo.session.query(Patient).filter(Patient.doctor_id == doctor_id).count()
                if count_doc >= 5:
                    available_docs = self.get_available_doctors()
                    if available_docs:
                        doctor_id = available_docs[0].id
                    else:
                        continue 

            self.add_patient(
                name=row['PatientName'],
                birth_date=row['DateOfBirth'],
                blood_type=row['BloodType'],
                doctor_id=doctor_id,
                ward_id=ward_id
            )

    def get_all_patients(self, page: int = 1, limit: int = 20):
        return self._data_repo.get_all_patients(page, limit)

    def get_patient_by_id(self, patient_id: int):
        return self._data_repo.get_patient_by_id(patient_id)

    def get_all_doctors(self):
        return self._data_repo.get_all_doctors()

    def get_all_wards(self):
        return self._data_repo.get_all_wards()

    def add_patient(self, name: str, birth_date: str, blood_type: str, doctor_id: int = None, ward_id: int = None):
        year, month, day = birth_date.split('-')
        if len(year) > 4:
            birth_date = f"{year[:4]}-{month}-{day}"
            
        date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        mr = MedicalRecord(blood_type=blood_type, diagnosis="Новий пацієнт", allergies="Невідомо")
        new_patient = Patient(name=name, date_of_birth=date_obj, medical_record=mr, doctor_id=doctor_id, ward_id=ward_id)
        
        self._data_repo.add_patient(new_patient)

        if ward_id:
            count = self._data_repo.count_patients_in_ward(ward_id)
            if count >= 4:
                self._data_repo.update_ward_status(ward_id, False)

    def update_patient(self, patient_id: int, new_name: str, new_birth_date: str, blood_type: str, doctor_id: int = None, ward_id: int = None):
        patient = self._data_repo.get_patient_by_id(patient_id)
        if patient:
            old_ward_id = patient.ward_id
            
            patient.name = new_name
            patient.date_of_birth = datetime.strptime(new_birth_date, "%Y-%m-%d").date()
            if patient.medical_record:
                patient.medical_record.blood_type = blood_type
            
            patient.doctor_id = doctor_id
            patient.ward_id = ward_id
            
            self._data_repo.update_patient(patient)

            if old_ward_id != ward_id:

                if old_ward_id:
                    count_old = self._data_repo.count_patients_in_ward(old_ward_id)
                    if count_old < 4:
                        self._data_repo.update_ward_status(old_ward_id, True)

                if ward_id:
                    count_new = self._data_repo.count_patients_in_ward(ward_id)
                    if count_new >= 4:
                        self._data_repo.update_ward_status(ward_id, False)

    def delete_patient(self, patient_id: int):
        patient = self._data_repo.get_patient_by_id(patient_id)
        ward_id = patient.ward_id if patient else None

        self._data_repo.delete_patient(patient_id)

        if ward_id:
            count = self._data_repo.count_patients_in_ward(ward_id)
            if count < 4:
                self._data_repo.update_ward_status(ward_id, True)

    def get_free_wards(self):
        return self._data_repo.get_free_wards()
    
    def clear_all_patients(self):
        self._data_repo.clear_all_patients()

    def get_available_doctors(self, current_doctor_id=None):
        return self._data_repo.get_available_doctors(current_doctor_id)