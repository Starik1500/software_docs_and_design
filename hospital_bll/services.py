from datetime import datetime
from hospital_dal.interfaces import IDataRepository
from hospital_dal.models import Ward, Doctor, Patient, MedicalRecord
from .interfaces import IHospitalService

class HospitalService(IHospitalService):
    def __init__(self, data_repository: IDataRepository):
        self._data_repo = data_repository

    def process_and_save_data(self, csv_file_path: str):
        raw_data = self._data_repo.read_data_from_file(csv_file_path)

        wards_dict = {}
        doctors_dict = {}
        patients = []

        for row in raw_data:
            w_num = int(row['WardNumber'])
            if w_num not in wards_dict:
                wards_dict[w_num] = Ward(ward_number=w_num, floor=w_num // 100, is_free=False)

            d_name = row['DoctorName']
            if d_name not in doctors_dict:
                doctors_dict[d_name] = Doctor(name=d_name, specialization="Загальна практика")

            mr = MedicalRecord(blood_type=row['BloodType'], diagnosis="Очікує на обстеження", allergies="Невідомо")
            
            p = Patient(
                name=row['PatientName'],
                date_of_birth=datetime.strptime(row['DateOfBirth'], "%Y-%m-%d").date(),
                ward=wards_dict[w_num],
                doctor=doctors_dict[d_name],
                medical_record=mr
            )
            patients.append(p)

        self._data_repo.save_data_to_database(patients, list(wards_dict.values()), list(doctors_dict.values()))