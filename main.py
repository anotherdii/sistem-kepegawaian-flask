from flask import Flask, render_template, request, redirect, flash, session, url_for
from flaskext.mysql import MySQL
import pymysql
from datetime import datetime
from datetime import date
import mysql.connector

app = Flask(__name__)
app.secret_key = 'rahasia'
db=MySQL(host="localhost", user="root", passwd="", db="dbtokoa")
db.init_app(app)

@app.template_filter('date')
def format_date_filter(value, format="%Y-%m-%d"):
    if value == 'now':
        return datetime.now().strftime(format)
    # Jika kamu ingin memformat objek date/datetime lainnya
    if isinstance(value, (date, datetime)):
        return value.strftime(format)
    return value # Return original value if not a date or 'now'

db_config = {
    'host': 'localhost',  # Sesuaikan jika host MySQL kamu berbeda
    'user': 'root',       # Ganti dengan username MySQL kamu
    'password': '', # Ganti dengan password MySQL kamu
    'database': 'dbtokoa'
}

@app.route('/')
def index():
    return render_template('user/index.html')

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cursor = db.get_db().cursor()
            cursor.execute("SELECT id, username, password, hak_akses FROM user WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()

            if user:
                session['loggedin'] = True
                session['id'] = user[0]            # id
                session['username'] = user[1]      # username
                session['hak_akses'] = user[3]     # hak_akses

                if session['hak_akses'] == 'admin':
                    return redirect(url_for('home'))
                elif session['hak_akses'] == 'user':
                    return redirect(url_for('user_dashboard'))  # gunakan nama fungsi dashboard

                else:
                    flash("Hak akses tidak dikenal", "warning")
                    return redirect(url_for('login'))

            else:
                flash('Username atau password salah!', 'danger')
                return redirect(url_for('login'))

        except Exception as e:
            flash(f'Terjadi kesalahan: {e}', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
   
    if request.method == 'POST':
        if str(request.form['password'])!=str(request.form['konfirmasipassword']):
            flash('password dan konfirmasi password tidak cocok!', 'danger')
            return redirect('/register')
        username = request.form['username']
        password = request.form['password']
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM user where username=%s",(username,))
        data = cursor.fetchone()
        if data:
            flash('Maaf, username sudah ada!', 'danger')
            return redirect('/register')
        else:
            cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password))
            db.get_db().commit()

            flash('Berhasil! Silakan login menggunakan username dan password yang didaftarkan.', 'success')
            return redirect('/login')

    return render_template('register.html')

@app.route('/tentang')
def tentang():
    return render_template('user/tentang.html')

@app.route('/kontak')
def kontak():
    return render_template('user/kontak.html')


#  admin

@app.route('/admin/home')
def home():
    if 'loggedin' not in session or session['hak_akses'] != 'admin':
        return redirect('/login')

    conn = None
    cursor = None
    dashboard_data = {} # Dictionary untuk menyimpan semua data dashboard

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Total Laporan
        cursor.execute("SELECT COUNT(id) AS total_laporan FROM laporan")
        dashboard_data['total_laporan'] = cursor.fetchone()['total_laporan']

        # 2. Laporan Status 'Terkirim'
        cursor.execute("SELECT COUNT(id) AS laporan_terkirim FROM laporan WHERE status = 'Terkirim'")
        dashboard_data['laporan_terkirim'] = cursor.fetchone()['laporan_terkirim']

        # 3. Laporan Status 'Sukses'
        cursor.execute("SELECT COUNT(id) AS laporan_sukses FROM laporan WHERE status = 'Sukses'")
        dashboard_data['laporan_sukses'] = cursor.fetchone()['laporan_sukses']

        # 4. Laporan Terbaru (misalnya 5 laporan terakhir)
        cursor.execute("SELECT id, judul_laporan, tanggal, status FROM laporan ORDER BY tanggal DESC, id DESC LIMIT 5")
        dashboard_data['laporan_terbaru'] = cursor.fetchall()
        
        # Tambahan: Jumlah Pengguna (jika ada tabel 'users' dan ingin menampilkan)
        cursor.execute("SELECT COUNT(id) AS total_users FROM laporan")
        dashboard_data['total_users'] = cursor.fetchone()['total_users']


    except mysql.connector.Error as err:
        flash(f"Terjadi kesalahan database saat memuat dashboard: {err}", 'error')
        print(f"Error loading dashboard data: {err}") # Cetak error ke konsol Flask
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
    # Render template dengan data dashboard
    return render_template('/admin/index.html', dashboard_data=dashboard_data)

    

@app.route('/admin/admin-kelola-barang')
def kelolabarang():
    data=[]
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM barang")
        data = cursor.fetchall()
    except Exception as e:
        flash(f"Gagal mengambil data: {e}", "danger")
    return render_template('admin/barang.html', hasil=data)


@app.route('/admin/form-tambah-barang', methods=['GET', 'POST'])
def formbarang():
    if request.method == 'POST':
        nama = request.form['nama']
        nip = request.form['nip']
        jabatan = request.form['jabatan']
        unit_kerja = request.form['unit_kerja']
        alamat = request.form['alamat']
        try:
            cursor = db.get_db().cursor()
            sql = "INSERT INTO barang (nama, nip, jabatan, unit_kerja, alamat) VALUES (%s, %s, %s, %s, %s)"
            val = (nama, nip, jabatan, unit_kerja, alamat)
            print(val)
            cursor.execute(sql, val)
            db.get_db().commit()
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan data: {e}', 'danger')
        

        flash("Data barang berhasil ditambahkan!", "success")
        return redirect('/admin/admin-kelola-barang')
    return render_template('admin/formbarang.html')


@app.route('/admin/form-edit-barang/<id>', methods=['GET', 'POST'])
def formeditbarang(id):
    if request.method == 'POST':
        nama = request.form['nama']
        nip = request.form['nip']
        jabatan = request.form['jabatan']
        unit_kerja = request.form['unit_kerja']
        alamat = request.form['alamat']
        try:
            cursor = db.get_db().cursor()
            sql = """
                UPDATE barang
                SET nama=%s, nip=%s, jabatan=%s, unit_kerja=%s, alamat=%s
                WHERE id=%s
            """
            val = (nama, nip, jabatan, unit_kerja, alamat,id)
            print(val)
            cursor.execute(sql, val)
            db.get_db().commit()
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan data: {e}', 'danger')
        

        flash("Data barang berhasil diupdate!", "success")
        return redirect('/admin/admin-kelola-barang')
    data=[]
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM barang where id=%s",(id))
        data = cursor.fetchone()
    except Exception as e:
        flash(f'Gagal mengambil data: {e}', 'danger')
        return redirect('/admin/admin-kelola-barang')
    return render_template('admin/formeditbarang.html', barang=data)


@app.route('/admin/hapus-barang/<int:id>', methods=['POST'])
def hapus_barang(id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("DELETE FROM barang WHERE id = %s", (id,))
        db.get_db().commit()
        flash("Pegawai berhasil dihapus.", "success")
    except Exception as e:
        flash(f"Gagal menghapus pegawai: {e}", "danger")
   

    return redirect('/admin/admin-kelola-barang')

@app.route('/admin/hapus-user/<int:id>', methods=['POST'])
def hapus_user(id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("DELETE FROM user WHERE id = %s", (id,))
        db.get_db().commit()
        flash("User berhasil dihapus.", "success")
    except Exception as e:
        flash(f"Gagal menghapus user: {e}", "danger")
   

    return redirect('/admin/admin-kelola-user')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')




@app.route('/admin/admin-kelola-pengguna')
def kelolapengguna():
    data=[]
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM barang")
        data = cursor.fetchall()
    except Exception as e:
        flash(f"Gagal mengambil data: {e}", "danger")
    return render_template('admin/pengguna.html', hasil=data)



@app.route('/admin/admin-kelola-user')
def kelolauser():
    data=[]
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM user")
        data = cursor.fetchall()
    except Exception as e:
        flash(f"Gagal mengambil data: {e}", "danger")
    return render_template('admin/user.html', hasil=data)


@app.route('/admin/form-tambah-user', methods=['GET', 'POST'])
def formuser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hak_akses= request.form['hak_akses']
       
        try:
            cursor = db.get_db().cursor()
            sql = "INSERT INTO user (username, password, hak_akses) VALUES (%s, %s, %s)"
            val = (username, password, hak_akses)
            print(val)
            cursor.execute(sql, val)
            db.get_db().commit()
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan data: {e}', 'danger')
        

        flash("Data user berhasil ditambahkan!", "success")
        return redirect('/admin/admin-kelola-user')
    return render_template('admin/formuser.html')

@app.route('/admin/form-edit-user/<id>', methods=['GET', 'POST'])
def formedituser(id):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hak_akses= request.form['hak_akses']
       
        try:
            cursor = db.get_db().cursor()
            sql = """
                UPDATE user
                SET username=%s, password=%s, hak_akses=%s
                WHERE id=%s
            """
            val = (username, password, hak_akses, id)
            print(val)
            cursor.execute(sql, val)
            db.get_db().commit()
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan data: {e}', 'danger')
        

        flash("Data user berhasil diupdate!", "success")
        return redirect('/admin/admin-kelola-user')
    data=[]
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM user where id=%s",(id))
        data = cursor.fetchone()
    except Exception as e:
        flash(f'Gagal mengambil data: {e}', 'danger')
        return redirect('/admin/admin-kelola-user')
    return render_template('admin/formedituser.html', user=data)

@app.route('/user/dashboard')
def user_dashboard():
    if 'hak_akses' not in session or session['hak_akses'] != 'user':
        flash("Anda tidak memiliki izin mengakses halaman ini", "danger")
        return redirect(url_for('login'))

    data = None
    try:
        user_id = session.get('id')
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM barang WHERE id = %s", (user_id,))
            data = cursor.fetchone()
        connection.close()
    except Exception as e:
        flash(f"Gagal mengambil data: {e}", "danger")

    return render_template('user/pegawai.html', barang=data)

@app.route('/user/profil')
def profil():
    return render_template('user/profil.html')
@app.route('/user/ds')
def ds():
    return render_template('user/dashboard.html')
@app.route('/user/setting')
def setting():
    return render_template('user/setting.html')

@app.route('/laporan_kinerja', methods=['GET', 'POST'])
def laporan_kinerja():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # dictionary=True agar hasil query berupa dict

    if request.method == 'POST':
        judul_laporan = request.form['judul_laporan']
        tanggal_str = request.form['tanggal']
        status = request.form['status']

        # Konversi tanggal dari string (YYYY-MM-DD) ke objek date
        try:
            tanggal = date.fromisoformat(tanggal_str)
        except ValueError:
            flash('Format tanggal tidak valid. Gunakan YYYY-MM-DD.', 'error')
            return redirect(url_for('laporan_kinerja'))

        try:
            # Query untuk memasukkan data ke tabel 'laporan'
            # Pastikan kolom di tabel 'laporan' sesuai: id (auto-increment), judul_laporan, tanggal, status
            cursor.execute(
                "INSERT INTO laporan (judul_laporan, tanggal, status) VALUES (%s, %s, %s)",
                (judul_laporan, tanggal, status)
            )
            conn.commit()
            flash('Laporan kinerja berhasil ditambahkan!', 'success')
            return redirect(url_for('laporan_kinerja'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'error')
            conn.rollback() # Batalkan jika ada error
    
    # Ambil semua laporan untuk ditampilkan di tabel
    cursor.execute("SELECT * FROM laporan ORDER BY tanggal DESC, id DESC")
    laporan_data = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('laporan_kinerja.html', laporan_data=laporan_data)

@app.route('/admin/laporan_kinerja', methods=['GET'])
def admin_laporan_kinerja():
    # Proteksi rute: hanya admin yang bisa mengakses
    if 'hak_akses' not in session or session['hak_akses'] != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa mengelola laporan.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM laporan ORDER BY tanggal DESC, id DESC")
    laporan_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('/admin/admin_laporan_kinerja.html', laporan_data=laporan_data)

# In app.py

@app.route('/admin/edit_laporan/<int:laporan_id>', methods=['GET', 'POST'])
def admin_edit_laporan(laporan_id):
    if 'hak_akses' not in session or session['hak_akses'] != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa mengelola laporan.', 'error')
        return redirect(url_for('login'))

    conn = None # Inisialisasi koneksi dan kursor
    cursor = None
    laporan = None # Variabel untuk menyimpan data laporan yang akan diedit

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # Mengambil data sebagai dictionary

        if request.method == 'GET':
            # Ambil data laporan berdasarkan ID
            cursor.execute("SELECT id, judul_laporan, tanggal, status FROM laporan WHERE id = %s", (laporan_id,))
            laporan = cursor.fetchone() # Ambil satu baris data
            
            if not laporan: # Jika laporan tidak ditemukan
                flash('Laporan tidak ditemukan.', 'error')
                return redirect(url_for('admin_laporan_kinerja'))
            
            # Format tanggal ke string 'YYYY-MM-DD' agar kompatibel dengan input type="date"
            if isinstance(laporan['tanggal'], date):
                laporan['tanggal_str'] = laporan['tanggal'].isoformat()
            else:
                laporan['tanggal_str'] = '' # Atau tangani jika tanggal tidak valid
            
            # Tampilkan formulir edit dengan data laporan yang sudah ada
            return render_template('/admin/admin_edit_laporan.html', laporan=laporan)

        elif request.method == 'POST':
            # Ambil data dari formulir yang dikirim (POST)
            judul_laporan_baru = request.form['judul_laporan']
            tanggal_str_baru = request.form['tanggal']
            status_baru = request.form['status']

            # Validasi format tanggal
            try:
                tanggal_baru = date.fromisoformat(tanggal_str_baru)
            except ValueError:
                flash('Format tanggal tidak valid. Gunakan YYYY-MM-DD.', 'error')
                # Kembali ke halaman edit laporan yang sama
                return redirect(url_for('/admin/admin_edit_laporan', laporan_id=laporan_id)) 

            # Validasi status yang diizinkan (penting untuk keamanan)
            if status_baru not in ['Terkirim', 'Sukses']:
                flash('Status yang dipilih tidak valid.', 'error')
                # Kembali ke halaman edit laporan yang sama
                return redirect(url_for('admin_edit_laporan', laporan_id=laporan_id))

            # Lakukan UPDATE ke database
            cursor.execute(
                "UPDATE laporan SET judul_laporan = %s, tanggal = %s, status = %s WHERE id = %s",
                (judul_laporan_baru, tanggal_baru, status_baru, laporan_id)
            )
            conn.commit() # Simpan perubahan
            flash('Laporan kinerja berhasil diperbarui.', 'success')
            # Redirect kembali ke daftar laporan admin setelah berhasil
            return redirect(url_for('admin_laporan_kinerja'))

    except mysql.connector.Error as err:
        flash(f"Terjadi kesalahan database: {err}", 'error')
        if conn:
            conn.rollback() # Batalkan transaksi jika ada error
    finally:
        # Pastikan koneksi dan kursor selalu ditutup
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
    # Fallback return: Jika ada error tak terduga dan tidak ada redirect terjadi di atas
    return redirect(url_for('admin_laporan_kinerja'))


@app.route('/admin/update_laporan_status/<int:laporan_id>', methods=['POST'])
def update_laporan_status(laporan_id):
    if 'hak_akses' not in session or session['hak_akses'] != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa mengelola laporan.', 'error')
        return redirect(url_for('login'))
      
    
    new_status = request.form['status']
    
    if new_status not in ['Terkirim', 'Sukses']:
        flash('Status tidak valid.', 'error')
        return redirect(url_for('admin_laporan_kinerja'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE laporan SET status = %s WHERE id = %s",
            (new_status, laporan_id)
        )
        conn.commit()
        flash(f'Status laporan ID {laporan_id} berhasil diperbarui menjadi "{new_status}".', 'success')
    except mysql.connector.Error as err:
        flash(f"Error memperbarui status: {err}", 'error')
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
    return redirect(url_for('admin_laporan_kinerja'))

@app.route('/admin/delete_laporan/<int:laporan_id>', methods=['POST'])
def admin_delete_laporan(laporan_id):
    # Proteksi rute: hanya admin yang bisa mengakses
    if 'hak_akses' not in session or session['hak_akses'] != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa mengelola laporan.', 'error')
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Eksekusi perintah DELETE SQL
        cursor.execute("DELETE FROM laporan WHERE id = %s", (laporan_id,))
        conn.commit() # Simpan perubahan ke database
        flash(f'Laporan ID {laporan_id} berhasil dihapus.', 'success')
    except mysql.connector.Error as err:
        flash(f"Terjadi kesalahan database saat menghapus laporan: {err}", 'error')
        if conn:
            conn.rollback() # Batalkan transaksi jika ada error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
    # Redirect kembali ke daftar laporan admin setelah operasi
    return redirect(url_for('admin_laporan_kinerja'))

@app.route('/admin/bantuan')
def admin_bantuan():
    # Proteksi rute: hanya admin yang bisa mengakses
    if 'hak_akses' not in session or session['hak_akses'] != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa mengelola laporan.', 'error')
        return redirect(url_for('login'))

    # Data FAQ, email dukungan, dan fitur (bisa diperluas)
    faq_items = [
        {
            'question': 'Bagaimana cara menambahkan laporan kinerja baru?',
            'answer': 'Anda dapat menambahkan laporan kinerja melalui halaman "Kelola Laporan" lalu klik tombol "Tambah Laporan Baru". Isi formulir yang tersedia dan simpan.'
        },
        {
            'question': 'Bagaimana cara mengubah status laporan?',
            'answer': 'Pada halaman "Kelola Laporan", Anda bisa langsung mengubah status "Terkirim" menjadi "Sukses" melalui dropdown di kolom Status.'
        },
        {
            'question': 'Apa yang terjadi jika saya menghapus laporan?',
            'answer': 'Menghapus laporan akan secara permanen menghilangkan data laporan tersebut dari sistem. Pastikan Anda benar-benar yakin sebelum menghapus.'
        },
        {
            'question': 'Bagaimana cara memperbarui data laporan yang sudah ada?',
            'answer': 'Pada halaman "Kelola Laporan", klik tombol "Edit" di samping laporan yang ingin diubah. Anda dapat mengedit judul, tanggal, dan status laporan.'
        },
        # Tambahkan lebih banyak FAQ di sini
    ]

    fitur_utama = [
        'Manajemen Laporan Kinerja: Tambah, Lihat, Edit, Hapus laporan.',
        'Pembaruan Status Laporan Cepat: Ubah status laporan langsung dari daftar.',
        'Dashboard Administratif: Ringkasan statistik laporan dan pengguna.',
        'Sistem Autentikasi Pengguna: Login dan logout dengan hak akses berbeda.'
        # Tambahkan lebih banyak fitur di sini
    ]

    email_dukungan = 'support@sistemkepegawaian.com' # Ganti dengan email dukungan yang sebenarnya

    return render_template('/admin/bantuan.html',
                           faq_items=faq_items,
                           fitur_utama=fitur_utama,
                           email_dukungan=email_dukungan)

@app.route('/info_keluarga') # Tidak ada lagi <int:pegawai_id>
def admin_info_keluarga():
    if 'hak_akses' not in session or session['hak_akses'] != 'user':
        flash("Anda tidak memiliki izin mengakses halaman ini", "danger")
        return redirect(url_for('login'))

    # Data pegawai dan keluarga DI-HARDCODE (Statis)
    pegawai_contoh = {
        'id': 101,
        'nama_lengkap': 'Budi Santoso',
        'jabatan': 'Manajer Proyek',
        'divisi': 'Teknologi Informasi',
        'email': 'budi.s@example.com'
    }

    data_keluarga_statis = [
        {'hubungan': 'Istri', 'nama': 'Dewi Lestari', 'tanggal_lahir': '1985-07-12', 'pekerjaan': 'Desainer Grafis', 'telepon': '081234567890'},
        {'hubungan': 'Anak', 'nama': 'Putra Pratama', 'tanggal_lahir': '2010-03-25', 'pekerjaan': 'Pelajar', 'telepon': 'N/A'},
        {'hubungan': 'Anak', 'nama': 'Putri Ayu', 'tanggal_lahir': '2015-09-01', 'pekerjaan': 'Pelajar', 'telepon': 'N/A'},
    ]

    return render_template('admin_info_keluarga.html',
                           pegawai=pegawai_contoh,
                           data_keluarga=data_keluarga_statis)
      


@app.route('/sejarah_pendidikan')
def admin_sejarah_pendidikan():
    if 'hak_akses' not in session or session['hak_akses'] != 'user':
        flash("Anda tidak memiliki izin mengakses halaman ini", "danger")
        return redirect(url_for('login'))

    # Data pegawai dan sejarah pendidikan DI-HARDCODE (Statis)
    pegawai_contoh = {
        'id': 101,
        'nama_lengkap': 'Budi Santoso',
        'jabatan': 'Manajer Proyek',
        'divisi': 'Teknologi Informasi',
        'email': 'budi.s@example.com'
    }

    sejarah_pendidikan_statis = [
        {
            'tingkat': 'SD',
            'institusi': 'SD Negeri 01 Jakarta',
            'tahun_masuk': '1992',
            'tahun_lulus': '1998',
            'jurusan': 'N/A'
        },
        {
            'tingkat': 'SMP',
            'institusi': 'SMP Swasta Harapan',
            'tahun_masuk': '1998',
            'tahun_lulus': '2001',
            'jurusan': 'N/A'
        },
        {
            'tingkat': 'SMA',
            'institusi': 'SMA Negeri 5 Bandung',
            'tahun_masuk': '2001',
            'tahun_lulus': '2004',
            'jurusan': 'IPA'
        },
        {
            'tingkat': 'Sarjana (S1)',
            'institusi': 'Universitas Teknologi Jakarta',
            'tahun_masuk': '2004',
            'tahun_lulus': '2008',
            'jurusan': 'Teknik Informatika'
        }
    ]

    return render_template('sejarahpendidikan.html',
                           pegawai=pegawai_contoh,
                           sejarah_pendidikan=sejarah_pendidikan_statis)


# di app.py

# ... (kode impor, app setup, session, redirect, url_for, render_template, flash, dll.) ...

# --- Rute BARU: Halaman Riwayat Pekerjaan Admin (STATIS) ---
@app.route('/riwayat_pekerjaan')
def admin_riwayat_pekerjaan():
    if 'hak_akses' not in session or session['hak_akses'] != 'user':
        flash("Anda tidak memiliki izin mengakses halaman ini", "danger")
        return redirect(url_for('login'))

    # Data pegawai dan riwayat pekerjaan DI-HARDCODE (Statis)
    pegawai_contoh = {
        'id': 101,
        'nama_lengkap': 'Budi Santoso',
        'jabatan': 'Manajer Proyek',
        'divisi': 'Teknologi Informasi',
        'email': 'budi.s@example.com'
    }

    riwayat_pekerjaan_statis = [
        {
            'perusahaan': 'PT Jaya Abadi',
            'jabatan': 'Staf IT',
            'tanggal_mulai': '2008-07-01',
            'tanggal_selesai': '2012-12-31',
            'deskripsi': 'Bertanggung jawab atas pemeliharaan jaringan dan dukungan teknis.'
        },
        {
            'perusahaan': 'CV Maju Bersama',
            'jabatan': 'Supervisor IT',
            'tanggal_mulai': '2013-01-15',
            'tanggal_selesai': '2018-06-30',
            'deskripsi': 'Memimpin tim IT dan mengelola proyek-proyek infrastruktur.'
        },
        {
            'perusahaan': 'PT Inovasi Digital',
            'jabatan': 'Manajer Proyek',
            'tanggal_mulai': '2018-07-10',
            'tanggal_selesai': 'Sekarang', # atau '2025-06-11' jika ingin tanggal spesifik
            'deskripsi': 'Mengelola siklus hidup proyek pengembangan perangkat lunak.'
        }
    ]

    return render_template('pekerjaan.html',
                           pegawai=pegawai_contoh,
                           riwayat_pekerjaan=riwayat_pekerjaan_statis)


if __name__ == '__main__':
    app.run(debug=True)
