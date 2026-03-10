from abc import ABC, abstractmethod

class IPatientView(ABC):
    @abstractmethod
    def show_patient_info(self, patient_id: int): pass

class IWardView(ABC):
    @abstractmethod
    def show_free_wards(self): pass