from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import hospital_admissions, patients, vaccinations

index_date = "2022-06-01"

latest_vaccination = (
    vaccinations.take(vaccinations.date.add_days(30) <= index_date)
    .sort_by(vaccinations.date)
    .last_for_patient()
)
subsequent_admissions = hospital_admissions.take(
    (hospital_admissions.admission_date > latest_vaccination.date)
    & (hospital_admissions.admission_date <= latest_vaccination.date.add_days(30))
)

dataset = Dataset()
dataset.set_population(patients.date_of_birth < "2000-01-01")
dataset.vaccination_date = latest_vaccination.date
dataset.vaccination_product = latest_vaccination.product_name
dataset.has_admission = subsequent_admissions.exists_for_patient()
