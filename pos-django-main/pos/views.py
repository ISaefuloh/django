from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from pos.forms import BuatOrderForm, BayarOrderForm, MenuForm
from pos.models import Menu, Order, Item, Menu, Fitur
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from users.views import  bukan_level_kasir

@login_required
def home(request):
    return render(request, 'pos/home.html')

@login_required
def daftar_menu(request, order_id):
    menu_list = Menu.objects.all()
    order = get_object_or_404(Order, pk=order_id)

    page = request.GET.get('page', 1)
    
    paginator = Paginator(menu_list, 10)
    
    try:
        menus = paginator.page(page)
    except PageNotAnInteger:
        menus = paginator.page(1)
    except EmptyPage:
        menus = paginator.page(paginator.num_pages)
    
    return render(request, 
                  'pos/daftar_menu.html', 
                  {'menus': menus,
                   'order': order})

@login_required
def buat_order(request):
    if request.method == 'POST':
        form = BuatOrderForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.total = 0
            obj.dibayar = 0
            obj.kembali = 0
            obj.save()
            return redirect('pos:daftar-menu', order_id=obj.pk)

    else:
        form = BuatOrderForm()
    return render(request, 'pos/buat_order.html', {'form': form})

@login_required
def order_aktif(request):
    order_list = Order.objects.filter(selesai=False)
    page = request.GET.get('page', 1)
    paginator = Paginator(order_list, 10)

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request,
                  'pos/order_aktif.html',
                  {'orders': orders})

@login_required
def tambah_item(request, order_id, menu_id):
    order = get_object_or_404(Order, id=order_id)
    menu = get_object_or_404(Menu, id=menu_id)
    item, created = Item.objects.get_or_create(
        menu=menu,
        order=order
    )

    item.qty = item.qty + 0
    item.harga = menu.price
    item.subtotal = item.harga * item.qty
    item.save()

    items = Item.objects.filter(order=order).aggregate(total=Sum('subtotal'))
    order.total = items['total']
    order.save()

    return redirect('pos:daftar-menu', order_id=order.id)

@login_required
def tambah_qty(request, order_id, menu_id):
    order = get_object_or_404(Order, id=order_id)
    menu = get_object_or_404(Menu, id=menu_id)
    
    # Cek apakah item sudah ada dalam pesanan
    item = Item.objects.filter(menu=menu, order=order).first()
    
    if not item:
        # Menampilkan pesan error jika item belum ada
        messages.error(request, 'Item belum dipilih. Silakan pesan menu terlebih dahulu.')
        return redirect('pos:daftar-menu', order_id=order.id)
    
    # Jika item sudah ada, lakukan penambahan jumlah
    item.qty += 1
    item.harga = menu.price
    item.subtotal = item.harga * item.qty
    item.save()

    # Update total pada order
    items = Item.objects.filter(order=order).aggregate(total=Sum('subtotal'))
    order.total = items['total']
    order.save()

    return redirect('pos:daftar-menu', order_id=order.id)

@login_required
def kurangi_qty(request, order_id, menu_id):
    order = get_object_or_404(Order, id=order_id)
    menu = get_object_or_404(Menu, id=menu_id)
    
    # Cek apakah item sudah ada dalam pesanan
    item = Item.objects.filter(menu=menu, order=order).first()
    
    if not item:
        # Menampilkan pesan error jika item belum ada
        messages.error(request, 'Item belum dipilih. Silakan pesan menu terlebih dahulu.')
        return redirect('pos:daftar-menu', order_id=order.id)

    if item.qty <= 1:
        # Menampilkan pesan error jika kuantitas item tidak bisa dikurangi lebih lanjut
        messages.error(request, 'Tidak bisa mengurangi jumlah item lebih dari ini.')
        item.delete()  # Jika kuantitas 1, item dihapus
        return redirect('pos:daftar-menu', order_id=order.id)

    # Jika item sudah ada dan qty lebih dari 1, lakukan pengurangan
    item.qty -= 1
    item.harga = menu.price
    item.subtotal = item.harga * item.qty
    item.save()

    # Update total pada order
    items = Item.objects.filter(order=order).aggregate(total=Sum('subtotal'))
    order.total = items['total']
    order.save()

    return redirect('pos:daftar-menu', order_id=order.id)

@login_required
def batal_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('pos:order-aktif')

@login_required
def bayar_order(request, id):
    order = get_object_or_404(Order, id=id, selesai=False)

    if request.method == 'POST':
        form = BayarOrderForm(data=request.POST)

        if form.is_valid():
            dibayar = form.cleaned_data['dibayar']

            if dibayar < order.total:
                raise ValidationError('Uang Anda kurang!')

            order.kembali = dibayar - order.total
            order.dibayar = dibayar
            order.selesai = True
            order.save()

            return render(
                request,
                'pos/print_order.html',
                {'order': order}
            )

    else:
        form = BayarOrderForm()

    return render(request,
                  'pos/bayar_order.html',
                  {'order': order, 'form': form})

@login_required
def print_order(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'pos/print_order.html', {'order': order})

@login_required
def cetak_struk(request, id):
    # Ambil data pesanan berdasarkan ID
    order = get_object_or_404(Order, id=id)
    
    # Ambil semua item yang ada di pesanan
    items = Item.objects.filter(order=order)
    
    # Jika pesanan tidak memiliki item, tampilkan pesan error
    if not items:
        messages.error(request, "Order ini tidak memiliki item!")
        return redirect('pos:laporan-penjualan')
    
    # Render template cetak_struk.html untuk menampilkan struk
    return render(
        request,
        'pos/cetak_struk.html',  # Template yang akan menampilkan struk
        {'order': order, 'items': items}  # Data yang dikirim ke template
    )

@login_required
# Laporan Penjualan  
def laporan_penjualan(request):
    """
    # Cek apakah fitur 'laporan_penjualan' aktif
    fitur_laporan_penjualan = Fitur.objects.filter(nama="laporan_penjualan", aktif=True).exists()

    if not fitur_laporan_penjualan:
        # Jika fitur tidak aktif, tampilkan pesan atau redirect ke halaman lain
        messages.error(request, "Anda tidak memiliki akses ke Laporan Penjualan!!!")
        return redirect('pos:home')  # Contoh redireksi ke halaman home
    """
    # Cek apakah pengguna adalah bagian dari grup 'Level_Kasir'
    if request.user.groups.filter(name='Level_Kasir').exists():
        # Jika pengguna dalam grup 'Level_Kasir', hanya tampilkan laporan hari ini
        order = Order.objects.filter(tanggal=datetime.date.today())
        jumlah = sum(order.total for order in order)
        context = {'order': order, 'jumlah': jumlah}
        return render(request, 'pos/laporan_penjualan.html', context)

    # Pastikan form POST mengandung tanggal awal dan akhir
    if request.method == "POST":
        awal_tgl = request.POST.get('awal_tgl')
        akhir_tgl = request.POST.get('akhir_tgl')

        # Cek apakah tanggal awal dan akhir ada di inputan
        if not awal_tgl or not akhir_tgl:
            # Jika tanggal tidak diisi, tampilkan pesan error
            messages.error(request, 'Harap pilih tanggal mulai dan tanggal akhir terlebih dahulu.')
            return render(request, 'pos/laporan_penjualan.html')

        # Jika tanggal ada, lanjutkan dengan pemrosesan laporan
        order = Order.objects.filter(tanggal__range=[awal_tgl, akhir_tgl])
        jumlah = sum(order.total for order in order)
        context = {'order': order, 'jumlah': jumlah}
        return render(request, 'pos/laporan_penjualan.html', context)
    
    else:
        # Jika request tidak POST (misalnya GET), tampilkan laporan untuk hari ini
        order = Order.objects.filter(tanggal=datetime.date.today())
        jumlah = sum(order.total for order in order)
        context = {'order': order, 'jumlah': jumlah}
        return render(request, 'pos/laporan_penjualan.html', context)



### Kelola Menu : ###
# 1. Tambah Menu
@login_required
def tambah_menu(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            # Menyimpan data menu baru ke dalam database
            form.save()
            messages.success(request, 'Menu berhasil ditambahkan!')
            return redirect('pos:master-menu')  # Arahkan ke halaman daftar menu setelah menambah menu
    else:
        form = MenuForm()

    return render(request, 'pos/tambah_menu.html', {'form': form})

# 2. Hapus Menu
@login_required
def hapus_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)  # Mencari menu berdasarkan ID
    menu.delete()  # Menghapus menu dari database
    messages.success(request, 'Menu berhasil dihapus!')
    return redirect('pos:master-menu')  # Arahkan ke halaman daftar menu setelah menu dihapus

# 3. Edit Menu
@login_required
def edit_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)

    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)  # Mengisi form dengan data menu yang ada
        if form.is_valid():
            form.save()  # Simpan perubahan
            return redirect('pos:master-menu')  # Arahkan kembali ke daftar menu
    else:
        form = MenuForm(instance=menu)  # Jika bukan POST, tampilkan form dengan data yang sudah ada
    
    return render(request, 'pos/edit_menu.html', {'form': form, 'menu': menu})
###-----------------###

# Master Menu
@login_required
@user_passes_test(bukan_level_kasir, login_url='pos:home')  # Hanya pengguna bukan 'Level_Kasir' yang bisa mengakses
def master_menu(request):
    """
    # Cek apakah fitur 'master_menu' aktif
    fitur_master_menu = Fitur.objects.filter(nama="master_menu", aktif=True).exists()

    if not fitur_master_menu:
        messages.error(request, "Anda tidak memiliki akses ke MasterMenu!!!")
        return redirect('pos:home')  # Redirect jika fitur tidak aktif
    """
    # Cek apakah pengguna berada di grup Level_Kasir
    if request.user.groups.filter(name='Level_Kasir').exists():
        messages.error(request, "Anda tidak memiliki akses ke Master Menu.")
        return redirect('pos:home')  # Redirect ke halaman home jika grup Level_Kasir

    menu_list = Menu.objects.all()  # Ambil semua menu dari database
    
    # Paginasi: Menampilkan 10 menu per halaman
    page = request.GET.get('page', 1)
    paginator = Paginator(menu_list, 10)  # Setiap halaman menampilkan 10 menu
    
    try:
        menus = paginator.page(page)
    except PageNotAnInteger:
        menus = paginator.page(1)  # Jika page bukan integer, tampilkan halaman pertama
    except EmptyPage:
        menus = paginator.page(paginator.num_pages)  # Jika halaman lebih dari total halaman, tampilkan halaman terakhir
    
    return render(request, 'pos/master_menu.html', {'menus': menus})

### Kontrol Fitur : ###
# 1. View untuk menampilkan daftar fitur
def fitur_list(request):
    fitur = Fitur.objects.all()
    return render(request, 'pos/fitur_list.html', {'fitur': fitur})

# 2. View untuk mengaktifkan/non-aktifkan fitur
def fitur_toggle(request, fitur_id):
    fitur = Fitur.objects.get(id=fitur_id)
    fitur.aktif = not fitur.aktif  # Toggle status aktif
    fitur.save()
    return redirect('pos:fitur_list')  # Redirect kembali ke daftar fitur