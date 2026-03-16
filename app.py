import os
from flask import Flask, render_template, request, redirect, url_for, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hospital_dal.models import Base
from hospital_dal.repository import DataRepository
from hospital_bll.services import HospitalService
from main import generate_csv

app = Flask(__name__)

csv_path = "hospital_data.csv"
db_path = "sqlite:///hospital.db"

if not os.path.exists(csv_path):
    generate_csv(csv_path, 1000)

engine = create_engine(db_path)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

data_repo = DataRepository(db_session)
hospital_service = HospitalService(data_repo)

@app.route('/')
def index():
    patients_list = hospital_service.get_all_patients()

    return render_template('index.html', patients=patients_list)

BLOOD_TYPES = [
    "O(I) Rh+", "O(I) Rh-", 
    "A(II) Rh+", "A(II) Rh-", 
    "B(III) Rh+", "B(III) Rh-", 
    "AB(IV) Rh+", "AB(IV) Rh-"
]

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        blood_type = request.form['blood_type']
        
        doctor_id = request.form.get('doctor_id')
        ward_id = request.form.get('ward_id')
        
        if not doctor_id:
            return "Помилка: Лікар є обов'язковим!", 400
            
        doctor_id = int(doctor_id)
        ward_id = int(ward_id) if ward_id else None
        
        hospital_service.add_patient(name, birth_date, blood_type, doctor_id, ward_id)
        return redirect(url_for('index'))
    
    doctors = hospital_service.get_available_doctors()
    free_wards = hospital_service.get_free_wards()
    
    return render_template('add.html', doctors=doctors, wards=free_wards, blood_types=BLOOD_TYPES)


@app.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = hospital_service.get_patient_by_id(patient_id)
    
    if request.method == 'POST':
        new_name = request.form['name']
        new_birth_date = request.form['birth_date']
        blood_type = request.form['blood_type']
        
        doctor_id = request.form.get('doctor_id')
        ward_id = request.form.get('ward_id')
        
        doctor_id = int(doctor_id) if doctor_id else patient.doctor_id
        ward_id = int(ward_id) if ward_id else None
        
        hospital_service.update_patient(patient_id, new_name, new_birth_date, blood_type, doctor_id, ward_id)
        return redirect(url_for('index'))
        
    doctors = hospital_service.get_available_doctors(patient.doctor_id)
    free_wards = hospital_service.get_free_wards()
    
    wards_for_dropdown = list(free_wards)
    if patient.ward and patient.ward not in wards_for_dropdown:
        wards_for_dropdown.append(patient.ward)
        
    return render_template('edit.html', patient=patient, doctors=doctors, wards=wards_for_dropdown, blood_types=BLOOD_TYPES)

@app.route('/delete/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    hospital_service.delete_patient(patient_id)
    return redirect(url_for('index'))

@app.route('/load-more-patients', methods=['GET'])
def load_more_patients():
    page = int(request.args.get('page', 1))

    patients = hospital_service.get_all_patients(page=page, limit=20)

    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "date_of_birth": str(p.date_of_birth),
            "ward_number": p.ward.ward_number if p.ward else None,
            "doctor_name": p.doctor.name if p.doctor else None,
            "blood_type": p.medical_record.blood_type if p.medical_record else None
        })
        
    return jsonify(result), 200

@app.route('/clear-db', methods=['POST'])
def clear_db():
    hospital_service.clear_all_patients()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)