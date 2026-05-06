import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

def cleanup():
    tables_to_drop = [
        'appointments_prescribedmedicine',
        'appointments_prescription',
        'appointments_medicine',
    ]
    with connection.cursor() as cursor:
        # Disable foreign key checks to ensure tables can be dropped in any order
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table};")
                print(f"Dropped table {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

if __name__ == "__main__":
    cleanup()
