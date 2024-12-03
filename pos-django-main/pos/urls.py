from django.urls import path
from pos import views

app_name = 'pos'

urlpatterns = [
    path('home', views.home, name='home'),
    path('new-order/', views.buat_order, name='buat-order'),
    path('daftar-menu/<int:order_id>/', views.daftar_menu, name='daftar-menu'),
    path('tambah-item/<int:order_id>/<int:menu_id>/', views.tambah_item, name='tambah-item'),
    path('kurangi-qty/<int:order_id>/<int:menu_id>/', views.kurangi_qty, name='kurangi-qty'),
    path('tambah-qty/<int:order_id>/<int:menu_id>/', views.tambah_qty, name='tambah-qty'),
    path('order-aktif/', views.order_aktif, name='order-aktif'),
    path('print-order/<int:id>/', views.print_order, name='print-order'),
    path('batal-order/<int:id>/', views.batal_order, name='batal-order'),
    path('bayar-order/<int:id>/', views.bayar_order, name='bayar-order'),
    path('laporan-penjualan/', views.laporan_penjualan, name='laporan-penjualan'),

    # URL untuk fungsi cetak_struk
    path('cetak-struk/<int:id>/', views.cetak_struk, name='cetak-struk'),  
    # URL untuk menambah menu
    path('menu/tambah/', views.tambah_menu, name='tambah-menu'),
    # URL untuk menghapus menu
    path('menu/hapus/<int:menu_id>/', views.hapus_menu, name='hapus-menu'),
    # URL untuk edit menu
    path('menu/edit/<int:menu_id>/', views.edit_menu, name='edit-menu'),
    # Master Menu
    path('master-menu/', views.master_menu, name='master-menu'),
    # Kontrol Fitur
    path('fitur/', views.fitur_list, name='fitur_list'),  # Daftar fitur
    path('fitur/toggle/<int:fitur_id>/', views.fitur_toggle, name='fitur_toggle'),  # Toggle fitur aktif/non-aktif

]
