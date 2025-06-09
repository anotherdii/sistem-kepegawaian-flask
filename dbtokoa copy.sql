-- Buat database jika belum ada
CREATE DATABASE IF NOT EXISTS dbtokoa;
USE dbtokoa;

-- DROP semua tabel jika sebelumnya sudah ada
DROP TABLE IF EXISTS dokumen;
DROP TABLE IF EXISTS laporan_kinerja;
DROP TABLE IF EXISTS cuti;
DROP TABLE IF EXISTS absensi;
DROP TABLE IF EXISTS barang;
DROP TABLE IF EXISTS user;

-- Tabel USER (akun login)
CREATE TABLE user (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(191) NOT NULL,
  password VARCHAR(191) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dummy user admin
INSERT INTO user (username, password) VALUES ('admin', 'admin123');

-- Tabel BARANG (pegawai)
CREATE TABLE barang (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  nama VARCHAR(50) NOT NULL,
  nip INT NOT NULL,
  jabatan VARCHAR(100) NOT NULL,
  unit_kerja VARCHAR(50) NOT NULL,
  deskripsi TEXT,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel ABSENSI
CREATE TABLE absensi (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  barang_id INT NOT NULL,
  tanggal DATE,
  jam_masuk TIME,
  jam_pulang TIME,
  status ENUM('Hadir', 'Izin', 'Sakit', 'Alpha'),
  keterangan TEXT,
  FOREIGN KEY (barang_id) REFERENCES barang(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel CUTI
CREATE TABLE cuti (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  barang_id INT NOT NULL,
  tanggal_pengajuan DATE,
  tanggal_mulai DATE,
  tanggal_selesai DATE,
  alasan TEXT,
  status ENUM('Menunggu', 'Disetujui', 'Ditolak') DEFAULT 'Menunggu',
  FOREIGN KEY (barang_id) REFERENCES barang(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel LAPORAN KINERJA
CREATE TABLE laporan_kinerja (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  barang_id INT NOT NULL,
  periode VARCHAR(20),
  deskripsi TEXT,
  file_laporan VARCHAR(255),
  status ENUM('Menunggu', 'Disetujui', 'Revisi') DEFAULT 'Menunggu',
  tanggal_upload DATETIME,
  FOREIGN KEY (barang_id) REFERENCES barang(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel DOKUMEN
CREATE TABLE dokumen (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  barang_id INT NOT NULL,
  nama_dokumen VARCHAR(100),
  file VARCHAR(255),
  tanggal_upload DATETIME,
  FOREIGN KEY (barang_id) REFERENCES barang(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
