

Project ini merupakan aplikasi **Backend API + Frontend sederhana**
untuk manajemen data butik pakaian.

## Fitur Utama
- Autentikasi & otorisasi (Admin, Owner, Kasir, Pelanggan)
- CRUD:
  - Produk
  - Pelanggan
  - Supplier
  - Karyawan
  - Users
  - Transaksi & Detail Transaksi
  - Pembelian & Detail Pembelian
- Rate limiting & throttling
- Middleware global (JWT & Session)
- Frontend HTML + JavaScript (login & dashboard)

## Teknologi
- Backend: Python Flask
- Database: SQL Server
- Auth: JWT + Session
- Rate limit: Flask-Limiter
- Frontend: HTML & JavaScript

## Cara Menjalankan
### Backend
```bash
python app.py
```
### Frontend
```
cd frontend
python -m http.server 8000
```


### Akses
Frontend: http://127.0.0.1:8000
Backend API: http://127.0.0.1:5000
Dokumentasi API: http://127.0.0.1:5000/docs
