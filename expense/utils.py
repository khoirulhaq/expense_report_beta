import csv
from .models import Expense

def import_csv_data(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Expense.objects.create(
                tanggal=row['Tanggal'],
                kategori=row['Kategori'],
                nominal=row['Nominal'],
                catatan=row['Catatan'],
                prioritas=row['Prioritas'],
                dompet=row['Dompet']
            )
