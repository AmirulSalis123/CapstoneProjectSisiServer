NAMA   : AMIRUL SALIS
NIM    : A11.2022.14258
KELP   : A11.4604
MATKUL : PEMOGRAMAN SISI SERVER

# Simple LMS - Proyek Akhir Backend

Repositori ini merupakan implementasi backend dari sistem Simple Learning Management System (LMS) menggunakan Django dan Django Ninja sebagai REST API Framework. Sistem ini mendukung fitur pendaftaran pengguna, manajemen kursus, komentar, sertifikat penyelesaian, pelacakan progres konten, dan statistik aktivitas pengguna.

# Tujuan Proyek

Tujuan dari proyek ini adalah membangun backend dari platform e-learning sederhana yang dapat:
Mengelola pengguna dan peran (teacher dan student)
Mengatur kursus dan kontennya
Mengelola enrollment peserta
Memberikan fitur tracking penyelesaian konten
Memberikan sertifikat jika kursus telah selesai
Menyediakan statistik aktivitas pengguna dan kursus

# Teknologi yang Digunakan

Python 3.11
Django sebagai web framework utama
Django Ninja untuk REST API
Django Ninja JWT untuk autentikasi berbasis token
PostgreSQL sebagai database utama
Docker & Docker Compose untuk manajemen layanan
HTML Template (certificate)
Swagger UI untuk dokumentasi endpoint otomatis

# Fitur dan Endpoint yang Sudah Diselesaikan

1. Register User (1 Poin)
   Endpoint: POST /api/v1/register
   Pengguna baru dapat mendaftar dengan data login dan biodata (username, nama, email, password).
   Validasi tersedia untuk mengecek apakah username atau email sudah digunakan.

2. Batch Enroll Students (1 Poin)
   Endpoint: POST /api/v1/course/batch-enroll
   Teacher dapat menambahkan beberapa siswa ke kursus sekaligus dengan menyertakan daftar user ID.
   Terdapat validasi agar siswa tidak bisa didaftarkan dua kali dan pengecekan batas maksimal siswa (kuota).

3. Content Comment Moderation (1 Poin)
   Endpoint: POST /api/v1/comment/moderate
   Teacher dapat menyetujui atau menolak komentar yang muncul di konten kursusnya.
   Komentar yang belum disetujui tidak akan tampil di endpoint publik GET /comments/{content_id}.

4. User Activity Dashboard (1 Poin)
   Endpoint: GET /api/v1/user/activity
   Menampilkan statistik aktivitas pengguna:
   Total kursus yang diikuti
   Total kursus yang dibuat (sebagai teacher)
   Total komentar yang dibuat
   Total konten yang diselesaikan (jika fitur completion aktif)

5. Course Analytics (1 Poin)
   Endpoint: GET /api/v1/course/analytics
   Menampilkan statistik untuk semua kursus milik teacher:
   Jumlah member
   Jumlah konten
   Jumlah komentar
   Jumlah komentar yang disetujui

6. Content Scheduling (1 Poin)
   Konten memiliki field available_at, di mana konten hanya akan muncul setelah waktu yang dijadwalkan.
   Endpoint: GET /course/{course_id}/available-contents hanya mengembalikan konten yang available_at <= now.

7. Course Enrollment Limits (1 Poin)
   Teacher dapat menetapkan max_students saat membuat kursus.
   Sistem akan menghitung jumlah siswa terdaftar sebelum menambahkan siswa baru.
   Jika kuota penuh, siswa tidak bisa ditambahkan.

8. Course Completion Certificate (3 Poin)
   Endpoint:
   POST /course/{course_id}/complete: Menandai kursus telah selesai oleh siswa.
   GET /course/{course_id}/certificate: Menampilkan sertifikat HTML kepada siswa.
   Sertifikat menampilkan nama siswa, nama kursus, dan tanggal penyelesaian.
   Hanya siswa yang menyelesaikan kursus yang bisa mengaksesnya.

9. Manajemen Profil Pengguna (2 Poin)
   Tampilkan Profil:
   Endpoint: GET /user/{user_id}/profile
   Menampilkan nama, email, nomor HP, deskripsi, foto, kursus yang dibuat dan diikuti.
   Edit Profil:
   Endpoint: PUT /user/edit-profile
   User bisa mengubah nama, email, handphone, deskripsi, dan upload foto profil.

10. Content Completion Tracking (3 Poin)
    Add Completion:
    Endpoint: POST /content/{content_id}/complete
    Siswa menandai konten sebagai selesai.
    Show Completion:
    Endpoint: GET /course/{course_id}/completed-contents
    Menampilkan konten-konten yang telah diselesaikan oleh siswa.
    Delete Completion:
    Endpoint: DELETE /content/{content_id}/complete
    Menghapus status penyelesaian pada konten tertentu.

# Autentikasi
Sistem menggunakan JWT berbasis Django Ninja Simple JWT.
Login menggunakan endpoint: /api/v1/auth/token
Gunakan token dengan header:
Authorization: Bearer <access_token>
