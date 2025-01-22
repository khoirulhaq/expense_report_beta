from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Makanan/Minuman", "Makanan/Minuman"),
        ("Komunikasi", "Komunikasi"),
        ("Transportasi", "Transportasi"),
        ("Pendidikan/Ilmu", "Pendidikan/Ilmu"),
        ("Hiburan", "Hiburan"),
        ("Kesehatan", "Kesehatan"),
        ("Kebersihan", "Kebersihan"),
        ("Belanja", "Belanja"),
        ("Darurat", "Darurat"),
        ("Tempat tinggal", "Tempat tinggal"),
        ("Produktivitas", "Produktivitas"),
        ("Lainnya", "Lainnya"),
    ]

    PRIORITY_CHOICES = [
        ("Butuh", "Butuh"),
        ("Harus", "Harus"),
        ("Ingin", "Ingin"),
    ]

    WALLET_CHOICES = [
        ("Cash", "Cash"),
        ("OVO", "OVO"),
        ("BJB", "BJB"),
        ("Livin", "Livin"),
        ("ShopeePay", "ShopeePay"),
        ("Lainnya", "Lainnya"),
    ]

    tanggal = models.DateField()
    kategori = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    nominal = models.DecimalField(max_digits=10, decimal_places=2)
    catatan = models.TextField()
    prioritas = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    dompet = models.CharField(max_length=10, choices=WALLET_CHOICES)

    def __str__(self):
        return f"{self.tanggal} - {self.kategori} - Rp {self.nominal}"
