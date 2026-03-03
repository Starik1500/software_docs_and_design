from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Ward(Base):
    __tablename__ = 'wards'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ward_number = Column(Integer, unique=True)
    floor = Column(Integer)
    is_free = Column(Boolean, default=False)
    
    patients = relationship("Patient", back_populates="ward")

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    specialization = Column(String)
    
    patients = relationship("Patient", back_populates="doctor")

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date_of_birth = Column(Date)
    
    ward_id = Column(Integer, ForeignKey('wards.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    
    ward = relationship("Ward", back_populates="patients")
    doctor = relationship("Doctor", back_populates="patients")
    medical_record = relationship("MedicalRecord", back_populates="patient", uselist=False, cascade="all, delete-orphan")

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    blood_type = Column(String)
    diagnosis = Column(String)
    allergies = Column(String)
    
    patient_id = Column(Integer, ForeignKey('patients.id'))
    patient = relationship("Patient", back_populates="medical_record")