from django.db import migrations

def seed_medicines(apps, schema_editor):
    Medicine = apps.get_model('appointments', 'Medicine')
    medicines_to_add = [
        {"name": "Paracetamol", "description": "Used to treat pain and fever.", "stock": 500},
        {"name": "Amoxicillin", "description": "Antibiotic used to treat various bacterial infections.", "stock": 200},
        {"name": "Ibuprofen", "description": "Nonsteroidal anti-inflammatory drug (NSAID) used for pain and inflammation.", "stock": 350},
        {"name": "Cetirizine", "description": "Antihistamine used to treat allergy symptoms.", "stock": 150},
        {"name": "Metformin", "description": "First-line medication for the treatment of type 2 diabetes.", "stock": 400},
        {"name": "Atorvastatin", "description": "Statin medication used to prevent cardiovascular disease and treat abnormal lipid levels.", "stock": 300},
        {"name": "Omeprazole", "description": "Proton-pump inhibitor used to treat gastroesophageal reflux disease (GERD).", "stock": 250},
        {"name": "Azithromycin", "description": "Antibiotic used for the treatment of a number of bacterial infections.", "stock": 180},
        {"name": "Losartan", "description": "Medication used to treat high blood pressure.", "stock": 220},
        {"name": "Salbutamol", "description": "Medication that opens up the medium and large airways in the lungs.", "stock": 100},
        {"name": "Aspirin", "description": "Used to reduce pain, fever, or inflammation.", "stock": 600},
        {"name": "Lisinopril", "description": "ACE inhibitor used to treat high blood pressure and heart failure.", "stock": 280},
        {"name": "Levothyroxine", "description": "Thyroid hormone used to treat thyroid hormone deficiency.", "stock": 190},
        {"name": "Gabapentin", "description": "Used to treat partial seizures and nerve pain.", "stock": 140},
        {"name": "Amlodipine", "description": "Calcium channel blocker used to treat high blood pressure and chest pain.", "stock": 310},
    ]
    for med_data in medicines_to_add:
        Medicine.objects.get_or_create(
            name=med_data["name"],
            defaults={"description": med_data["description"], "stock": med_data["stock"]}
        )

def remove_medicines(apps, schema_editor):
    Medicine = apps.get_model('appointments', 'Medicine')
    Medicine.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0004_alter_appointment_date_alter_appointment_status_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_medicines, reverse_code=remove_medicines),
    ]
