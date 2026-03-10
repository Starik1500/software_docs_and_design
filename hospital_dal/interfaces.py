from abc import ABC, abstractmethod

class IDataRepository(ABC):
    @abstractmethod
    def read_data_from_file(self, file_path: str) -> list[dict]:
        pass

    @abstractmethod
    def save_data_to_database(self, patients, wards, doctors):
        pass