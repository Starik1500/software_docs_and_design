from abc import ABC, abstractmethod

class IHospitalService(ABC):
    @abstractmethod
    def process_and_save_data(self, csv_file_path: str):
        pass