import os
import csv
import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hospital_dal.models import Base
from hospital_dal.repository import DataRepository
from hospital_bll.services import HospitalService

def generate_csv(file_path, count=45):
    import csv
    import random
    from faker import Faker
    
    print(f"Генеруємо файл на {count} рядків...")
    fake = Faker('uk_UA')
    ward_numbers = [101, 102, 103, 104, 201, 202, 203, 301, 305]
    doctor_names = [
        "Dr. Старик", "Dr. Батіг", "Dr. Грибовський", "Dr. Кравченко", "Dr. Грабар", "Dr. Шевченко", "Dr. Мельник", "Dr. Мороз", "Dr. Сатана", "Dr. Савченко"
    ]
    
    blood_types = [
        "O(I) Rh+", "O(I) Rh-", "A(II) Rh+", "A(II) Rh-", 
        "B(III) Rh+", "B(III) Rh-", "AB(IV) Rh+", "AB(IV) Rh-"
    ]

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["PatientName", "DateOfBirth", "BloodType", "WardNumber", "DoctorName"])
        for _ in range(count):
            writer.writerow([
                fake.name(),
                fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d"),
                random.choice(blood_types),
                random.choice(ward_numbers),
                random.choice(doctor_names)
            ])

if __name__ == "__main__":
    csv_path = "hospital_data.csv"
    db_path = "sqlite:///hospital.db"

    if not os.path.exists(csv_path):
        generate_csv(csv_path, 45)

    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Налаштування IoC та DI...")
    data_repo = DataRepository(session)
    hospital_service = HospitalService(data_repo)

    print("Починаємо вичитування даних з файлу та збереження в БД...")
    try:
        hospital_service.process_and_save_data(csv_path)
        print("ГОТОВО! Всі дані успішно збережено в базу даних SQLite (hospital.db).")
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        session.close()