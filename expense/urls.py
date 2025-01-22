from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('import/', views.import_csv_data, name='import_csv_data'),
    path('add/', views.expense_form, name='expense_add'),
    path('edit/<int:id>/', views.expense_form, name='expense_edit'),
    path('delete/<int:id>/', views.expense_delete, name='expense_delete'),
    path('export_csv/', views.export_expenses_csv, name='export_csv'),



    # URL untuk Menu Statistik
    path('statistik/', views.menu_2, name='menu_2'),  
    path('api/expense-data/', views.get_expense_data, name='get_expense_data'),  # URL untuk mendapatkan data pengeluaran
    path('clear-expenses/', views.clear_expenses, name='clear_expenses'),  # URL untuk menghapus semua pengeluaran

    # URL untuk Menu Analisis
    path('analisis/', views.menu_analisis, name='menu_analisis'),
    
    path('get_daily_expenses/', views.get_daily_expenses, name='get_daily_expenses'),
    path('api/expenses-for-table/', views.get_expenses_for_table, name='get_expenses_for_table'),
    

]
