from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from django.core.paginator import Paginator
from .utils import import_csv_data
import csv
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Avg
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import pandas as pd

# ========= MENU ANALISIS ======

def menu_analisis(request):
    return render(request, 'expenses/menu_analisis.html')

def get_daily_expenses(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Ambil data dari database
    expenses = Expense.objects.filter(tanggal__range=[start_date, end_date])

    # Convert ke DataFrame untuk analisis
    df = pd.DataFrame(list(expenses.values('tanggal', 'nominal', 'kategori', 'dompet', 'prioritas')))
    
    # Pastikan kolom nominal adalah tipe float
    df['nominal'] = pd.to_numeric(df['nominal'], errors='coerce')

    # Hapus baris yang memiliki nilai NaN di kolom nominal
    df = df.dropna(subset=['nominal'])

    # Pastikan kolom tanggal adalah tipe datetime
    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')

    # Hapus baris yang memiliki nilai NaT (Not a Time)
    df = df.dropna(subset=['tanggal'])

    # Jika DataFrame kosong, return data kosong
    if df.empty:
        return JsonResponse({
            'dates': [],
            'totals': [],
            'average_per_day': [],
            'category_labels': [],
            'category_values': [],
            'wallet_labels': [],
            'wallet_values': [],
            'priority_labels': [],
            'priority_values': [],
        })

    # Agregasi per hari, hanya menjumlahkan kolom nominal
    daily_totals = df.groupby('tanggal')['nominal'].sum().reset_index()
    daily_totals['tanggal'] = daily_totals['tanggal'].astype(str)

    # Menghitung rata-rata pengeluaran per hari (dari Senin - Minggu)
    daily_totals['day_of_week'] = pd.to_datetime(daily_totals['tanggal']).dt.day_name()
    average_per_day = daily_totals.groupby('day_of_week')['nominal'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).fillna(0)

    # Hitung total untuk donut chart, hanya menjumlahkan kolom nominal
    category_totals = df.groupby('kategori')['nominal'].sum().reset_index()
    category_totals = category_totals.sort_values(by='nominal', ascending=False)
    wallet_totals = df.groupby('dompet')['nominal'].sum().reset_index()
    priority_totals = df.groupby('prioritas')['nominal'].sum().reset_index()

    return JsonResponse({
        'dates': daily_totals['tanggal'].tolist(),
        'totals': daily_totals['nominal'].tolist(),
        'average_per_day': average_per_day.tolist(),  # Rata-rata pengeluaran per hari
        'category_labels': category_totals['kategori'].tolist(),
        'category_values': category_totals['nominal'].tolist(),
        'wallet_labels': wallet_totals['dompet'].tolist(),
        'wallet_values': wallet_totals['nominal'].tolist(),
        'priority_labels': priority_totals['prioritas'].tolist(),
        'priority_values': priority_totals['nominal'].tolist(),
    })

def get_expenses_for_table(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    expenses = Expense.objects.filter(tanggal__range=[start_date, end_date]).values(
        'tanggal', 'kategori', 'nominal', 'catatan'
    )

    return JsonResponse(list(expenses), safe=False)


# ========= MENU STATISTIK ======

def menu_2(request):
    return render(request, 'expenses/menu_2.html')

def get_expense_data(request):
    # Ambil semua data pengeluaran dari database
    expenses_qs = Expense.objects.all().values('kategori', 'nominal', 'tanggal', 'prioritas', 'dompet')
    
    # Konversi queryset ke DataFrame pandas
    df = pd.DataFrame(list(expenses_qs))
    
    # Jika DataFrame kosong, return data kosong
    if df.empty:
        return JsonResponse({
            'months': [],
            'monthly_totals': [],
            'categories': [],
            'totals': [],
            'priorities': [],
            'priority_totals': [],
            'priority_percentages': [],
            'wallets': [],
            'wallet_totals': [],
            'wallet_percentages': [],
            'total_expense': 0,
            'average_expense': 0,
            'median_expense': 0,
        })

    # 1. Pengeluaran per bulan
    df['month'] = pd.to_datetime(df['tanggal']).dt.to_period('M')  # Ekstraksi bulan
    monthly_totals = df.groupby('month')['nominal'].sum().reset_index()
    monthly_totals['month'] = monthly_totals['month'].dt.strftime('%Y-%m')

    # 2. Pengeluaran per kategori
    category_totals = df.groupby('kategori')['nominal'].sum().reset_index()
    category_totals_expense = category_totals['nominal'].sum()
    category_totals['percentage'] = ((category_totals['nominal'] / category_totals_expense) * 100).apply(lambda x: round(x, 2))  # Membulatkan ke 2 angka di belakang koma

    # 3. Pengeluaran per prioritas
    priority_totals = df.groupby('prioritas')['nominal'].sum().reset_index()
    total_priority_expense = priority_totals['nominal'].sum()
    priority_totals['percentage'] = ((priority_totals['nominal'] / total_priority_expense) * 100).apply(lambda x: round(x, 2))  # Membulatkan ke 2 angka di belakang koma

    # 4. Pengeluaran per dompet
    wallet_totals = df.groupby('dompet')['nominal'].sum().reset_index()
    total_wallet_expense = wallet_totals['nominal'].sum()
    wallet_totals['percentage'] = ((wallet_totals['nominal'] / total_wallet_expense) * 100).apply(lambda x: round(x, 2))  # Membulatkan ke 2 angka di belakang koma

    # 5. Statistik pengeluaran per bulan
    total_expense = df['nominal'].sum()
    monthly_average_expense = monthly_totals['nominal'].mean()  # Rata-rata per bulan
    monthly_median_expense = monthly_totals['nominal'].median()  # Median per bulan

    # Membuat data JSON
    data = {
        'months': monthly_totals['month'].tolist(),
        'monthly_totals': monthly_totals['nominal'].round(2).tolist(),  # Membulatkan ke 2 angka di belakang koma
        'categories': category_totals['kategori'].tolist(),
        'totals': category_totals['nominal'].round(2).tolist(),  # Membulatkan ke 2 angka di belakang koma
        'priorities': priority_totals['prioritas'].tolist(),
        'priority_totals': priority_totals['nominal'].round(2).tolist(),  # Membulatkan ke 2 angka di belakang koma
        'priority_percentages': priority_totals['percentage'].tolist(),  # Persentase prioritas
        'category_percentages': category_totals['percentage'].tolist(),  # Persentase prioritas
        'wallets': wallet_totals['dompet'].tolist(),
        'wallet_totals': wallet_totals['nominal'].round(2).tolist(),  # Membulatkan ke 2 angka di belakang koma
        'wallet_percentages': wallet_totals['percentage'].tolist(),  # Persentase dompet
        'total_expense': float(round(total_expense, 2)),  # Membulatkan total pengeluaran
        'average_expense': round(monthly_average_expense, 2),  # Rata-rata per bulan
        'median_expense': round(monthly_median_expense, 2),    # Median per bulan
    }

    return JsonResponse(data)

# ========= MENU IMPORT DATA ======

# Import data CSV
def import_data(request):
    import_csv_data('path_to_csv_file.csv')  # Lokasi file CSV
    return redirect('expense_list')


def clear_expenses(request):
    if request.method == 'POST':  # Pastikan hanya bisa dihapus dengan POST
        Expense.objects.all().delete()  # Menghapus semua data
    return redirect('expense_list')  # Mengarahkan kembali ke daftar pengeluaran




# ========= MENU HOME ======

# List expenses dengan pagination
def expense_list(request):
    expenses = Expense.objects.all().order_by('-tanggal')
    paginator = Paginator(expenses, 10)  # Pagination dengan 5 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'expenses/expense_list.html', {'page_obj': page_obj})

# Tambah atau edit expense
def expense_form(request, id=None):
    if id:
        expense = get_object_or_404(Expense, id=id)
    else:
        expense = None

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/expense_form.html', {'form': form})

# Hapus expense
def expense_delete(request, id):
    expense = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


def import_csv_data(request):
    if request.method == "POST" and request.FILES["file"]:
        csv_file = request.FILES["file"]

        # Pastikan file adalah CSV
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("File tidak valid. Silakan unggah file CSV.")

        # Membaca file CSV
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        # Mengimpor data ke model Expense
        for row in reader:
            Expense.objects.create(
                tanggal=row['Tanggal'],
                kategori=row['Kategori'],
                nominal=row['Nominal'],
                catatan=row['Catatan'],
                prioritas=row['Prioritas'],
                dompet=row['Dompet']
            )
        return redirect('expense_list')  # Redirect ke daftar pengeluaran setelah impor

    return render(request, 'expenses/import_csv.html')  # Tampilkan halaman impor jika bukan POST


def export_expenses_csv(request):
    # Buat response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    # Buat writer CSV
    writer = csv.writer(response)
    # Header CSV
    writer.writerow(['Tanggal', 'Kategori', 'Nominal', 'Catatan', 'Prioritas', 'Dompet'])

    # Ambil data dari model Expense
    expenses = Expense.objects.all()

    # Loop dan tuliskan setiap row ke CSV
    for expense in expenses:
        writer.writerow([expense.tanggal, expense.kategori, expense.nominal, expense.catatan, expense.prioritas, expense.dompet])

    return response