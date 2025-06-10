from flask import Flask, render_template, request, redirect, flash, session, url_for
from flaskext.mysql import MySQL
import pymysql
app = Flask(__name__)
app.secret_key = 'rahasia'
db=MySQL(host="localhost", user="root", passwd="", db="dbtokoa")
db.init_app(app)

@app.route('/')
def index():
    return render_template('user/index.html')

def dbuser():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='dbtokoa',
        cursorclass=pymysql.cursors.DictCursor)

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
    return render_template('admin/index.html')
    

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
        connection = dbuser()
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





if __name__ == '__main__':
    app.run(debug=True)
