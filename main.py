from flask import Flask, render_template, request, redirect, flash, session, url_for
from flaskext.mysql import MySQL
app = Flask(__name__)
app.secret_key = 'rahasia'
db=MySQL(host="localhost", user="root", passwd="", db="dbtokoa")
db.init_app(app)

@app.route('/')
def index():
    return render_template('user/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.get_db().cursor()
        cursor.execute("SELECT id, username, password, hak_akses FROM user WHERE username=%s and password=%s",(username,password))
        data = cursor.fetchone()
        if data:
           
            session['loggedin'] = True
            session['id'] = data[0]
            session['username'] = data[1]    
            session['hak_akses'] = data[3]

        
            if session['hak_akses'] == 'admin':
                return redirect(url_for('home')) 
            else:
                return redirect(url_for('user')) 
        else:
            flash('Username atau password salah!', 'danger')
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
        deskripsi = request.form['deskripsi']
        try:
            cursor = db.get_db().cursor()
            sql = "INSERT INTO barang (nama, nip, jabatan, unit_kerja, deskripsi) VALUES (%s, %s, %s, %s, %s)"
            val = (nama, nip, jabatan, unit_kerja, deskripsi)
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
        deskripsi = request.form['deskripsi']
        try:
            cursor = db.get_db().cursor()
            sql = """
                UPDATE barang
                SET nama=%s, nip=%s, jabatan=%s, unit_kerja=%s, deskripsi=%s
                WHERE id=%s
            """
            val = (nama, nip, jabatan, unit_kerja, deskripsi,id)
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
        flash("Barang berhasil dihapus.", "success")
    except Exception as e:
        flash(f"Gagal menghapus barang: {e}", "danger")
   

    return redirect('/admin/admin-kelola-barang')


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
            val = (username, password,id, hak_akses)
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
def user():
    return render_template('user/pegawai.html')

if __name__ == '__main__':
    app.run(debug=True)
