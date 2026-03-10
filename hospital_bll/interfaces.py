from abc import ABC, abstractmethod

class IHospitalService(ABC):
    @abstractmethod
    def process_and_save_data(self, csv_file_path: str):
        pass

    @abstractmethod
    def get_all_patients(self):
        pass

    @abstractmethod
    def get_patient_by_id(self, patient_id: int):
        pass
    
    @abstractmethod
    def add_patient(self, name: str, birth_date: str, blood_type: str):
        pass

    @abstractmethod
    def update_patient(self, patient_id: int, new_name: str, new_birth_date: str):
        pass
    
    @abstractmethod
    def delete_patient(self, patient_id: int):
        pass