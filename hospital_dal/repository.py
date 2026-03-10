import csv
from sqlalchemy.orm import Session
from .interfaces import IDataRepository
from .models import Ward, Doctor, Patient

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