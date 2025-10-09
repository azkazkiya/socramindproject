# app/learning/routes.py
import os
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app, flash
from ..models.models import db, User, ConversationLog, QuizAnswer, QuizAttempt, UserProgress
from openai import OpenAI
from werkzeug.security import generate_password_hash

client = OpenAI(
    api_key=os.getenv("GOKU_API_KEY"),
    base_url=os.getenv("GOKU_BASE_URL")
)

curriculum = {
    'algoritma': [
        {
            'step': 0, 
            'title': 'Pendahuluan', # JUDUL BARU
            'type': 'socratic_question', 
            'is_concludable': True,
            'ct': 'Interpretasi', 
            'opening_message': "Halo! Saya SocraMind, tutor AI Anda. Mari kita mulai dengan pertanyaan pertama: Menurutmu, apa arti dari algoritma?",
            'instruction': """
            Tugas Anda adalah memulai percakapan dan mengevaluasi pemahaman awal siswa tentang 'algoritma'.
            2. Analisis jawaban PERTAMA dari siswa dan respons sesuai kondisi berikut:
                - JIKA siswa menjawab benar atau cukup masuk akal: Beri respons non-validasi untuk memancing diskusi. Contoh: "Oh begitu ya, coba jelaskan lebih lanjut maksudmu." (Ini akan memicu jawaban kedua dari siswa, JANGAN gunakan [SELESAI])".
                - JIKA siswa menjawab salah: Beri respons ini secara persis: "Hmm apakah benar begitu? ayo kita pastikan bersama-sama setelah ini!" dan WAJIB akhiri dengan sinyal `[SELESAI]`.
                - JIKA siswa menjawab 'tidak tahu', 'belum belajar', atau sejenisnya: Beri respons ini secara persis: "tidak apa-apa, ayoo kita pelajari terlebih dahulu bersama sama" dan WAJIB akhiri dengan sinyal `[SELESAI]`.
            3. JIKA Anda meminta jawaban kedua (karena jawaban pertama bagus): Setelah siswa memberikan jawaban KEDUA, berikan respons penutup singkat seperti 'Sip, mari kita pastikan bersama setelah ini yaa!' dan WAJIB akhiri dengan sinyal `[SELESAI]`.
            """
        },
        {
            'step': 1, 
            'title': 'Materi Algoritma dan Pemrograman', # JUDUL BARU
            'type': 'static_content', 
            'content_file': 'materi/algoritma_pengertian.html' 
        },
        {
            'step': 2, 
            'title': 'Klarifikasi Pemahaman', # JUDUL BARU
            'type': 'multi_stage_socratic', 
            'is_concludable': True,
            'ct': 'Interpretasi, Analisis, Evaluasi, Inferensi, Eksplanasi, Regulasi Diri', 
            'opening_message': "Oke, sekarang setelah membaca materi, coba jelaskan kembali apa itu algoritma dengan bahasamu sendiri.",
            'instruction': """
            Tugas Anda adalah memandu siswa memperdalam pemahaman tentang 'algoritma' melalui 6 tujuan Socratic secara berurutan. Anda yang mengontrol alur percakapan.
            ATURAN SANGAT PENTING UNTUK LANGKAH INI:
            - Ajukan HANYA SATU pertanyaan pada satu waktu. Tunggu jawaban siswa sebelum melanjutkan ke pertanyaan atau tujuan berikutnya. Jangan menggabungkan beberapa pertanyaan dalam satu pesan.
            - Pada kalimat penutup JANGAN SEBUTKAN 6 TUJUAN SOCRATIC secara langsung
            ALUR KERJA WAJIB:
            1. Setelah siswa memberikan jawaban awal, pandu mereka melalui 6 pertanyaan socratic ini, SATU PER SATU:
                - Tujuan 1: Klarifikasi (Pastikan definisinya jelas).
                - Tujuan 2: Menyelidiki Asumsi (Tantang asumsi di balik definisinya).
                - Tujuan 3: Menyelidiki Alasan dan Bukti (Tantang mereka untuk memberikan alasan ataupun bukti dibalik asumsi sebelumnya)
                - Tujuan 4: Menyelidiki Implikasi dan Konsekuensi
                - Tujuan 5: Menyelidiki Sudut Pandang dan Perspektif lain
                - Tujuan 6: Memastikan kembali pertanyaan tiap pertanyaan
            2. ATURAN ADAPTIF PALING PENTING:
                - Anda HARUS TETAP di tujuan saat ini sampai Anda menilai pemahaman siswa sudah cukup baik.
                - JIKA siswa menjawab salah, 'tidak tahu', atau bingung pada tujuan saat ini (misalnya, di Tujuan 1: Klarifikasi), maka pertanyaan atau petunjuk Anda berikutnya HARUS TETAP bertujuan untuk Klarifikasi. JANGAN pindah ke Tujuan 2: Menyelidiki Asumsi.
                - Contoh: Jika di Tujuan 1 siswa bingung, berikan analogi (seperti resep masakan atau rute GPS) untuk membantu mengklarifikasi, BUKAN untuk menyelidiki asumsi.
            3. Setelah Anda yakin sebuah tujuan tercapai, barulah Anda boleh pindah ke tujuan berikutnya dengan transisi yang alami.
            4. Setelah semua 6 tujuan tercapai, akhiri respons terakhir dengan kalimat penutup dan WAJIB diakhiri dengan sinyal `[SELESAI]`.
            """,
        },
        {
            'step': 3,
            'title': 'Tipe Data', # JUDUL BARU
            'type': 'multi_stage_socratic',
            'is_concludable': True,
            'ct': 'Interpretasi, Analisis',
            'opening_message': "Bagus sekali! Sekarang kita sudah lebih paham tentang algoritma, mari kita bahas 'bahan baku'-nya, yaitu Tipe Data. Pernah dengar istilah itu?",
            'illustration_image': 'Tipe-Data.jpg',
            'instruction': """
            Tugas Anda adalah memandu siswa memahami konsep Tipe Data dan Operator Aritmatika dasar melalui 4 tujuan Socratic. Anda yang mengontrol alur percakapan.
            ATURAN SANGAT PENTING UNTUK LANGKAH INI: JANGAN BERI VALIDASI seperti "Benar" atau "Tepat Sekali" dan sebagainya apabila percakapan belum mencapai akhir.
            1. Setelah siswa menjawab pertanyaan pembuka, pandu mereka secara berurutan melalui 4 tujuan ini:
                - Tujuan 1: Dasar & Contoh (Klarifikasi definisi Tipe Data dan minta contoh).
                - Tujuan 2: Penggunaan & Konsekuensi (Bahas penggunaan praktis dan akibat jika salah pakai).
                - Tujuan 3: Pengenalan Operator (Hubungkan Tipe Data dengan operator yang bisa digunakan).
                - Tujuan 4: Sudut Pandang lain dan Refleksi (Tutup dengan pertanyaan meta).
            2. ATURAN ADAPTIF: Jika siswa bingung di satu tujuan, tetaplah di tujuan itu dan berikan petunjuk. Jangan pindah ke tujuan berikutnya sampai siswa cukup paham.
            3. ALUR KHUSUS TUJUAN 3 (OPERATOR):
                a. Mulai dengan pertanyaan pancingan. Contoh: "Oke, kita sudah punya 'wadah' (variabel) dan 'isi' (tipe data). Sekarang, bagaimana cara kita 'mengolah' isi tersebut? Misalnya, jika kita punya dua variabel angka, `a = 10` dan `b = 5`, simbol apa yang kita gunakan untuk menjumlahkannya?"
                b. Setelah siswa menjawab (jawaban: `+`), berikan pertanyaan Socratic yang menantang. Contoh: "Tepat. Sekarang, apa yang terjadi jika kita menggunakan simbol `+` yang sama pada dua data bertipe teks, misalnya `'Halo' + 'Dunia'`? Apakah hasilnya akan sama dengan penjumlahan angka?"
                c. Pandu diskusi singkat ini untuk menyimpulkan bahwa fungsi operator bisa berbeda tergantung tipe datanya.
            4. Setelah semua 4 tujuan tercapai, akhiri respons terakhir dengan kalimat penutup dan WAJIB diakhiri dengan sinyal [SELESAI].
            """,
        },
{
            'step': 4,
            'title': 'Prediksi & Eksekusi Program',
            'type': 'modify_code',
            'is_concludable': True, 
            'ct': 'Analisis & Evaluasi', 
            'primm': 'Predict, Run, Investigate',
            'hide_run_button_initially': True,
            'opening_message': "Oke, kita masuk ke tahap prediksi. Perhatikan kode di editor. Menurutmu apa output yang akan muncul?",
            'base_code': 'panjang = 10\nlebar = 5\nluas = panjang * lebar\nprint(f"Luas persegi panjang adalah: {luas}")',
            'instruction': """
            Tugas Anda adalah memandu siswa melalui alur Socratic Predict -> Investigate -> Run -> Evaluate.
            Jawaban output yang benar adalah "Luas persegi panjang adalah: 50".

            ALUR PERCAKAPAN WAJIB (ikuti langkah demi langkah):
            1.  Setelah siswa memberikan **prediksi awalnya**, jangan validasi. Tanyakan asumsi mereka. Contoh: "Oke, itu prediksimu. Apa yang mendasari pemikiranmu sampai ke jawaban itu?"
            2.  Setelah siswa memberikan **asumsinya**, minta bukti rasional. Contoh: "Bisa jelaskan lebih detail alasan logis di balik asumsimu itu?"
            3.  Setelah siswa memberikan **alasan logisnya**, instruksikan mereka untuk menjalankan kode dan WAJIB SERTAKAN sinyal `[TAMPILKAN_JALANKAN_KODE]` di akhir respons Anda. Contoh: "Baik, teorimu sudah kusimpan. Sekarang, silakan klik tombol 'Jalankan Kode' pada kode editor di atas. Apakah prediksimu sesuai dengan outputnya? [TAMPILKAN_JALANKAN_KODE]"
            4.  Setelah siswa memberitahu **output sebenarnya**, bandingkan dengan prediksi awal mereka di histori percakapan. Pilih salah satu dari dua alur di bawah ini:

                --> ALUR JIKA PREDIKSI SISWA BENAR (sesuai output):
                    a. Berikan penguatan positif. Tanyakan: "Tepat sekali! Prediksimu sama dengan hasilnya. Apa yang membuatmu begitu yakin dengan analisismu dari awal?"
                    b. Setelah siswa menjawab, ajukan pertanyaan implikasi & konsekuensi. Contoh: "Pemikiran yang bagus. Menurutmu, apa konsekuensinya jika kita lupa baris `print()` di akhir kode itu?"
                    c. Setelah siswa menjawab, berikan kalimat penutup dan WAJIB akhiri dengan sinyal [SELESAI].

                --> ALUR JIKA PREDIKSI SISWA SALAH (tidak sesuai output):
                    a. Arahkan perhatian pada perbedaan. Tanyakan: "Nah, sepertinya ada perbedaan antara prediksimu dengan hasil sebenarnya. Menurutmu, bagian mana dari kode yang membuat prediksimu keliru dan apa alasannya?"
                    b. Setelah siswa mencoba menganalisis kesalahannya, berikan penjelasan singkat dan jelas. Contoh: "Analisis yang bagus. Kesalahan umum terjadi saat .... Output yang benar adalah '50' karena variabel 'luas' menyimpan hasil perkalian 10 * 5."
                    c. Berikan kalimat penutup yang menyemangati dan WAJIB akhiri dengan sinyal [SELESAI].
            """
        },
        {
            'step': 5,
            'title': 'Investigasi Kode Program', # JUDUL BARU (dulu 'Investigate')
            'type': 'socratic_question',
            'is_concludable': True,
            'ct': 'Analisis',
            'opening_message': "Oke, disini kita akan bedah pola struktur kode. Kebanyakan program sederhana akan memiliki struktur seperti ini: **Input -> Proses -> Output**.\n\nCoba lihat kode ini:\n"
                            "<pre><code># Tahap Input\n"
                            "sisi = 10\n\n"
                            "# Tahap Proses\n"
                            "luas = sisi * sisi\n\n"
                            "# Tahap Output\n"
                            "print(luas)</code></pre>\n"
                            "Bisa jelaskan dengan bahasamu sendiri, apa yang terjadi di setiap tahap (Input, Proses, dan Output) pada kode itu?",
            'instruction': """
            Tugas Anda adalah memandu siswa memahami struktur dasar Input-Proses-Output dan Tipe Data.
            ALUR WAJIB:
            1.  Setelah siswa menjelaskan pemahamannya tentang Input-Proses-Output, ajukan pertanyaan pendalaman tentang **Tipe Data**. Tanyakan: "Penjelasan yang bagus! Kalau kita ingat materi Tipe Data, menurutmu, variabel `sisi` dan `luas` pada kode itu menyimpan tipe data apa ya?"
            2.  Setelah siswa menjawab (jawaban benar: integer/bilangan bulat), berikan pertanyaan lanjutan. Tanyakan pertanyaan implikasi dan konsekuensi: "Tepat sekali. Lalu, menurutmu apa yang akan terjadi pada hasil akhirnya jika nilai `sisi` kita ubah menjadi `10.5`?"
            3.  Setelah siswa menjawab pertanyaan kedua, berikan kalimat penutup yang menyimpulkan dan mengaitkan ke step berikutnya. Contoh: "Luar biasa! Kamu sudah paham bagaimana struktur dasar dan tipe data bekerja sama. Sekarang, ayo kita gunakan pemahaman ini untuk menganalisis kode yang sedikit lebih kompleks." dan WAJIB akhiri dengan sinyal [SELESAI].
            """
        },
        {
            'step': 6,
            'title': 'Modifikasi Kode Program', # JUDUL BARU
            'type': 'modify_code',
            'is_concludable': True,
            'ct': 'Analisis, Inferensi',
            'primm': 'Modify',
            'opening_message': "Kerja bagus! Sekarang kita coba tantangan logika. kode di atas merupakan program yang bertujuan untuk menukar isi dari 'gelasA' dan 'gelasB'. gelasA nantinya harus bernilai 20 dan gelasB bernilai 10. Coba jalankan programnya. Apakah outputnya sudah benar atau salah?",
            'base_code': "gelasA = 10  # Anggap berisi Kopi\ngelasB = 20  # Anggap berisi Teh\n\n# Mencoba menukar isi kedua gelas\ngelasA = gelasB\ngelasB = gelasA\n\nprint(f\"Isi Gelas A: {gelasA}, Isi Gelas B: {gelasB}\")",
            'instruction': """
            Tugas Anda adalah memandu siswa untuk menemukan solusi dalam masalah menukar nilai dua variabel.
            Konteks: Siswa melihat kode yang gagal menukar nilai (hasilnya kedua variabel akan sama).
            ALUR KERJA WAJIB:
            1.  **Tahap 1 (Analisis Awal)**: Setelah siswa memberikan hasil (yang seharusnya `Isi Gelas A: 20, Isi Gelas B: 20`), tanyakan mengapa isi Gelas A hilang dan kedua gelas menjadi sama.
            2.  **Tahap 2 (Permintaan Modifikasi)**: Gunakan analogi. Tanyakan, "Jika kamu punya segelas Kopi dan segelas Teh dan ingin menukar isinya, apa yang kamu butuhkan?". Bimbing dia untuk menemukan ide 'gelas kosong' atau variabel sementara. Minta dia untuk menambahkan variabel `temp` dan memperbaiki logikanya, lalu menjalankan kode lagi.
            3.  **Tahap 3 (Validasi & Penutup)**: Setelah siswa memberikan hasil yang benar (`Isi Gelas A: 20, Isi Gelas B: 10`), berikan validasi dan pujian atas kemampuannya memecahkan masalah logika ini. Akhiri dengan sinyal `[SELESAI]`.
            """
        },
        {
            'step': 7,
            'title': 'Membuat Kode Program', # JUDUL BARU
            'type': 'make_code',
            'is_concludable': True,
            'ct': 'Regulasi Diri',
            'primm': 'Make',
            'opening_message': "Kamu sudah sampai di tahap akhir! Saatnya membuat program dari nol. Studi kasusnya: Bayangkan kamu punya tiga barang dengan harga 500, 1200, dan 350. Buatlah program Python di editor untuk menghitung dan menampilkan total harga dari ketiga barang tersebut. Kemudian jelaskan kepadaku outputnya",
            'base_code': "# Tulis kodemu di sini...\n",
            'instruction': """
            Tugas Anda adalah memandu siswa melalui sesi refleksi setelah mereka membuat program.
            Konteks: Siswa baru saja membuat program untuk menghitung total harga dan telah memberitahu Anda hasilnya di chat.
            ALUR KERJA WAJIB:
            1.  **Mulai Sesi Refleksi**: JANGAN komentari benar atau salahnya hasil. Langsung ajukan pertanyaan reflektif pertama. Contoh: "Okee. Dari kode yang kamu buat, seberapa yakin kamu dengan solusimu? Apa yang membuatmu yakin atau mungkin kurang yakin?"
            2.  **Lanjutkan Refleksi**: Berdasarkan jawaban siswa, ajukan 1 hingga 3 pertanyaan pendalaman lagi yang tetap fokus pada proses berpikir mereka, bukan pada kebenaran kode. Contoh: "Bagian mana dari kodemu yang menurutmu paling menantang?", "Apakah ada cara lain yang kamu pertimbangkan untuk menyelesaikan masalah ini?"
            3.  **Validasi & Penutup**: Setelah sesi refleksi selesai (setelah 2-4 pertanyaan), berikan validasi dan kalimat penutup yang menyemangati. Contoh: "Diskusi yang bagus! Kemampuanmu untuk merefleksikan pekerjaanmu sendiri adalah skill penting seorang programmer. Kamu sudah menyelesaikan semua materi dasar!" dan WAJIB akhiri dengan sinyal `[SELESAI]`.
            """
        }
    ],
    'percabangan': [
        # Halaman 1 / Step 0: Interpretasi & Klarifikasi
         {
            'step': 0, 
            'title': 'Pendahuluan',
            'type': 'socratic_question', 
            'is_concludable': True,
            'ct': 'Interpretasi', 
            'opening_message': "Kita mulai ke topik berikutnya! Coba bayangkan situasi ini: 'Saat akan berangkat, kamu melihat ke luar jendela. JIKA langit mendung, MAKA kamu membawa payung.' Pola berpikir 'jika-maka' seperti ini sebenarnya punya nama khusus lho dalam logika. Menurutmu, ini termasuk pola atau kondisi apa ya?",
            'instruction': """
            Tugas Anda adalah memandu siswa memahami konsep 'percabangan' melalui analogi tanpa memberikan validasi langsung.
            ALUR WAJIB:
            1.  Saat siswa memberikan jawaban pertamanya (misal: 'percabangan'), JANGAN langsung memvalidasi. Alih-alih, gunakan respons netral untuk menyelidiki asumsi. Tanyakan: "Menarik sekali jawabanmu. Menurutmu, kenapa pola berpikir seperti itu penting dalam pengambilan keputusan sehari-hari?"
            2.  Setelah siswa menjawab pertanyaan kedua, minta mereka memberikan satu contoh sederhana lainnya. Tanyakan: "Oke, saya paham maksudmu. Coba berikan satu contoh lain yang mirip dari aktivitasmu sehari-hari."
            3.  Setelah siswa memberikan contoh, tutup dengan kalimat transisi: "Baik, kita simpan dulu ya, ayo kita masuk ke materinya!" dan WAJIB akhiri dengan sinyal [SELESAI].
            
            ATURAN TAMBAHAN:
            - JIKA jawaban siswa di awal 'tidak tahu', berikan respons seperti: "Tidak apa-apa, istilah ini memang spesifik. Ayo kita pelajari dulu bersama-sama!" dan akhiri dengan sinyal [SELESAI].
            - JIKA jawaban siswa salah atau diluar konteks, berikan respons seperti: "hmmmm benarkah begitu, sebaiknya ayo kita pelajari dulu bersama-sama!" dan akhiri dengan sinyal [SELESAI].
            """
        },
        # Halaman 2 / Step 1: Materi Statis
        {
            'step': 1, 
            'type': 'static_content', 
            'title': 'Materi: Konsep Struktur Kontrol Percabangan',
            'content_file': 'materi/percabangan_pengertian.html' 
        },
        
        # Halaman 3 / Step 2: Predict & Analisis Mendalam
        
        {
            'step': 2, 
            'title': 'Prediksi Kode Program',
            'type': 'predict_run_investigate',
            'is_concludable': True,
            'ct': 'Analisis', 
            'primm': 'Predict',
            'opening_message': "Sekarang kita analisis kode ini bersama. Kode ini bertujuan untuk memberikan diskon berdasarkan total belanja. Kira kira apa keluaran dari kode di atas ya?",
            'code': 'total_belanja = 125000\ndiskon = 0\n\nif total_belanja > 100000:\n    diskon = 0.1 # Diskon 10%\n\nharga_akhir = total_belanja - (total_belanja * diskon)\nprint(f"Harga setelah diskon: {harga_akhir}")',
            'instruction': """
            Tugas Anda adalah memandu siswa menganalisis dan memprediksi hasil kode melalui beberapa pertanyaan Socratic. JANGAN MEMBERI JAWABAN.
            ALUR WAJIB (tanyakan satu per satu):
            1. (Minta Prediksi Awal) Tanyakan: "Setelah memperhatikan kode di atas, menurutmu berapa `harga_akhir` yang akan ditampilkan?"
            2. (Pertanyaan Menyelidiki Alasan) Setelah siswa menjawab, tanyakan: "Oke, apa alasan di balik prediksimu itu?"
            3. (Pertanyaan Menyelidiki Implikasi dan Konsekuensi 1) Tanyakan: "Bagaimana jika baris `total_belanja = 125000` diubah menjadi `total_belanja = 95000`, berapa harga akhirnya sekarang?"
            4. (Pertanyaan Menyelidiki Implikasi dan Konsekuensi 2 - Error) Tanyakan: "Menarik. Terakhir, bagaimana jika baris `if total_belanja > 100000:` kita ubah menjadi `if total_belanja >`, apa yang akan terjadi?"
            5. (Minta Alasan Akhir) Setelah siswa menjawab (kemungkinan besar 'error' atau jawaban aneh), tanyakan pertanyaan asumsi: "Kenapa kamu berpikir hasilnya akan seperti itu?"
            6. Setelah siswa memberi alasan terakhir, tutup dengan kalimat: "Oke, kamu sudah siap untuk lanjut ke step berikutnya." dan akhiri dengan [SELESAI].
            """
        },
        # Halaman 4 / Step 3: Run & Investigate
        {
            'step': 3,
            'title': 'Menjalankan Program',
            'type': 'modify_code',
            'is_concludable': True,
            'ct': 'Evaluasi',
            'primm': 'Run, Investigate',
            'opening_message': "Mari kita buktikan prediksimu. Silakan jalankan kode di atas tanpa mengubah apa pun. Beritahu aku apa output kode di atas",
            'base_code': 'total_belanja = 125000\ndiskon = 0\n\nif total_belanja > 100000:\n    diskon = 0.1\n\nharga_akhir = total_belanja - (total_belanja * diskon)\nprint(f"Harga setelah diskon: {harga_akhir}")',
            'instruction': """
            Tugas Anda adalah memandu siswa mengevaluasi output program.
            ALUR WAJIB (tanyakan satu per satu):

            1. (Menyelidiki Klarifikasi) Setelah siswa mengetikkan output, tanyakan: "Apakah kamu percaya bahwa output tersebut sudah benar?"
            2. (Menyelidiki Alasan) Tanyakan: "Apa yang membuatmu yakin (atau tidak yakin) dengan kebenaran output itu?"
            3. (Pertanyaan Lanjutan) Berdasarkan respons siswa, ajukan satu pertanyaan lanjutan yang relevan untuk memperdalam pemahamannya.
            4. Setelah siswa menjawab, tutup percakapan dengan: "Diskusi yang bagus! Pemikiranmu sangat logis. Ayo kita lanjut." dan akhiri dengan [SELESAI].
            """
        },
        # Halaman 5 / Step 4: Investigate
        {
            'step': 4,
            'title': 'Investigasi',
            'type': 'socratic_question',
            'is_concludable': True,
            'ct': 'Analisis',
            
            'opening_message': "Nah, sekarang kita akan membedah kode, mari kita pahami 'resep' dasar penulisan percabangan. Lihat struktur umum ini ya:\n\n"
                            "<pre><code>if kondisi:\n"
                            "    # Lakukan sesuatu jika kondisi Benar</code></pre>\n"
                            "Menurutmu, bagian mana yang paling penting dari 'resep' di atas? 'if', 'kondisi', atau 'Lakukan sesuatu'?",
            'instruction': """
            Tugas Anda adalah memandu siswa untuk memahami setiap komponen dasar dari blok 'if'.
            ALUR WAJIB:
            1.  Setelah siswa menjawab (misal: 'kondisi'), minta mereka untuk menjelaskan alasannya. Tanyakan pertanyaan menyelidiki klarifikasi: "Menarik. Kenapa kamu memilih bagian itu sebagai yang paling penting?"
            2.  Setelah siswa memberi alasan, berikan pertanyaan Socratic lanjutan yang mengarahkan pada pentingnya komponen lain. Contoh: "Oke, masuk akal. Lalu, apa yang akan terjadi jika ada 'kondisi' tapi tidak ada kata kunci 'if' di depannya? Apakah komputer akan mengerti?"
            3.  Setelah siswa menjawab, ajukan pertanyaan terakhir tentang blok indented. Tanyakan: "Poin yang bagus. Terakhir, seberapa penting bagian '# Lakukan sesuatu' harus menjorok ke dalam (indentasi)?"
            4.  Setelah siswa menjawab, tutup dengan kalimat: "Kerja bagus! Sekarang kamu sudah paham anatomi dasarnya. Ayo kita lanjutkan!" dan WAJIB akhiri dengan sinyal [SELESAI].
            """
        },
        # Halaman 6 / Step 5: Modify, Eksplanasi & Inferensi
        {
            'step': 5,
            'title': 'Modifikasi Kode Program',
            'type': 'modify_code',
            'is_concludable': True,
            'ct': 'Eksplanasi, Inferensi',
            'primm': 'Modify',
            'opening_message': "Sekarang, perhatikan kode untuk menentukan status kelulusan di atas. Ayo coba klik Jalankan Kode untuk melihat hasilnya dan beritahu aku hasilnya!",
            'base_code': "nilai = 80\n\nif nilai >= 75:\n    status = 'Lulus'\nelse:\n    status = 'Gagal'\n\nprint(status)",
            'instruction': """
            Tugas Anda adalah memandu siswa memodifikasi kode dan menarik kesimpulan.
            ALUR WAJIB (tanyakan satu per satu):
            1. (Minta Modifikasi) Setelah siswa menjalankan kode dan memberitahukan outputnya di percakapan, minta dia memodifikasi kode program: "Oke sekarang coba kamu ubah nilai variabel `nilai` menjadi `60`, bagaimana hasilnya sekarang?"
            2. (Mencari Alternatif) Setelah siswa menjawab, ajukan tantangan: "Oke, jadi hasilnya 'Gagal' ya. Adakah alternatif cara lain untuk mendapatkan hasil yang sama ('Gagal') tanpa mengubah variabel `nilai=60`, tapi dengan mengubah kondisi `if`-nya?"
            3. (Menarik Kesimpulan) Setelah siswa menjawab (misal: `if nilai < 75`), tanyakan: "Tepat sekali! Jadi, apa kesimpulan yang bisa kita ambil dari percobaan ini tentang bagaimana sebuah kondisi `if-else` bekerja?"
            4. Setelah siswa memberikan kesimpulan, tutup dengan: "Kesimpulan yang bagus! Kamu berhasil menangkap intinya." dan akhiri dengan [SELESAI].
            """
        },
        # Halaman 7 / Step 6: Make - 1 Kondisi
        {
            'step': 6,
            'title': 'Membuat Kode Program Percabangan 1 Kondisi',
            'type': 'make_code',
            'is_concludable': True,
            'ct': 'Regulasi Diri',
            'primm': 'Make',
            'opening_message': "Kalau begitu aku punya tantangan buatmu: Buatlah kode program dari nol. Studi kasusnya: Sebuah toko buku memberikan diskon 5% jika total pembelian di atas Rp 200.000. Buatlah program untuk menghitung harga akhir jika diketahui `total_pembelian = 250000`. Beritahu aku jika sudah membuat programnya di atas",
            'base_code': "# Tulis kodemu di sini...\n",
            'instruction': """
            Tugas Anda adalah memandu refleksi siswa setelah membuat kode.
            1. Setelah siswa selesai dan menjalankan kodenya, ajukan pertanyaan reflektif: "Oke, dari kodemu, seberapa yakin kamu program itu akan berfungsi dengan benar jika `total_pembelian`-nya di bawah 200.000? Apa alasanmu?"
            2. Setelah siswa menjawab, akhiri dengan: "Bagus, kemampuan untuk memikirkan berbagai kemungkinan itu penting. Lanjut ke tantangan berikutnya!" dan sinyal [SELESAI].
            """
        },
        # Halaman 8 / Step 7: Make - 2 Kondisi
        {
            'step': 7,
            'title': 'Membuat Kode Program Percabangan 2 Kondisi',
            'type': 'make_code',
            'is_concludable': True,
            'ct': 'Regulasi Diri',
            'primm': 'Make',
            'opening_message': "Tantangan kedua: Buatlah program percabangan dua kondisi. Program dari nol untuk menentukan apakah sebuah angka adalah bilangan 'Positif' atau 'Negatif'. Anggap saja angka 0 kita masukkan ke kategori 'Positif'. Beritahu aku jika sudah membuat programnya di atas",
            'base_code': "# Tulis kodemu di sini...\n",
            'instruction': """
            Tugas Anda adalah memandu refleksi siswa setelah membuat kode.
            1. Setelah siswa selesai, ajukan pertanyaan: "Menurutmu, bagian mana dari kodemu yang paling krusial untuk memastikan semua angka ter-handle dengan benar (termasuk angka 0)?"
            2. Setelah siswa menjawab, akhiri dengan: "Tepat, pemilihan kondisi adalah kuncinya. Kerja bagus! Tinggal satu tantangan lagi." dan sinyal [SELESAI].
            """
        },
        # Halaman 9 / Step 8: Make - Lebih dari 2 Kondisi
        {
            'step': 8,
            'title': 'Membuat Kode Program Percabangan Lebih dari 2 Kondisi',
            'type': 'make_code',
            'is_concludable': True,
            'ct': 'Regulasi Diri',
            'primm': 'Make',
            'opening_message': "Tantangan terakhir: Buatlah program dari nol untuk menentukan kategori berat badan berdasarkan Indeks Massa Tubuh (IMT).\nAturan:\n- Jika IMT < 18.5, cetak 'Kurus'\n- Jika IMT antara 18.5 dan 24.9, cetak 'Normal'\n- Jika IMT >= 25, cetak 'Berlebih'. Beritahu aku jika sudah membuat programnya di atas",
            'base_code': "# Tulis kodemu di sini...\n",
            'instruction': """
            Tugas Anda adalah memandu refleksi siswa setelah membuat kode.
            1. Setelah siswa selesai, ajukan pertanyaan: "Bagian mana yang menurutmu paling sulit dan paling mudah?"
            2. Setelah siswa selesai menjawab, ajukan pertanyaan: "Jadi berdasarkan kode program yang telah dibuat, bagaimana kesimpulanmu?"
            3. Setelah siswa selesai menjawab, beri respon dari jawaban siswa dengan mengajukan pertanyaan socratic tipe Meta Pertanyaan (Regulasi Diri)
            2. Setelah siswa menjawab, berikan validasi dan pujian, lalu akhiri dengan: "Selamat, kamu telah menyelesaikan semua materi percabangan!" dan sinyal [SELESAI].
            """
        }
    ],
    'perulangan': [
        # Halaman 1 / Step 0: Interpretasi & Klarifikasi
        {
            'step': 0,
            'title': 'Pendahuluan',
            'type': 'socratic_question',
            'is_concludable': True,
            'ct': 'Interpretasi',
            'opening_message': "Mari kita mulai topik terakhir! Bayangkan kamu sedang mendengarkan lagu favoritmu dan kamu menyetelnya dalam mode 'repeat' atau 'ulang'. Menurutmu, konsep 'mengulang sesuatu berkali-kali' ini dalam pemrograman disebut apa ya?",
            'instruction': """
            Tugas Anda adalah memandu siswa memahami konsep 'perulangan' melalui analogi.
            ALUR WAJIB:
            1. Setelah siswa menjawab (misal: 'perulangan' atau 'looping'), berikan respons netral untuk menggali lebih dalam. Tanyakan: "Menarik. Menurutmu, kenapa kita butuh kemampuan untuk mengulang perintah di dalam program?"
            2. Setelah siswa memberi alasan, minta mereka memberikan satu contoh lain dari kehidupan sehari-hari dimana ada proses pengulangan.
            3. Setelah siswa memberikan contoh, tutup dengan kalimat transisi: "Contoh yang bagus! Konsepnya persis seperti itu. Ayo kita lihat materinya." dan WAJIB akhiri dengan sinyal [SELESAI].
            4. JIKA siswa tidak tahu, arahkan langsung ke materi dengan kalimat: "Tidak apa-apa, ini adalah konsep baru. Ayo kita pelajari bersama!" dan akhiri dengan [SELESAI].
            """
        },
        # Halaman 2 / Step 1: Materi Statis
        {
            'step': 1,
            'type': 'static_content',
            'title': 'Materi: Konsep Struktur Kontrol Perulangan',
            'content_file': 'materi/perulangan_pengertian.html'
        },
        
        # Halaman 3 / Step 2: Predict & Analisis Mendalam
        {
            'step': 2,
            'title': 'Prediksi',
            'type': 'predict_run_investigate',
            'is_concludable': True,
            'ct': 'Analisis',
            'primm': 'Predict',
            'opening_message': "Sekarang, coba perhatikan kode ini. Kode ini menggunakan `range()` untuk melakukan perulangan. Kira-kira apa outputnya?",
            'code': "for i in range(5):\n    print(i)", # Disesuaikan dengan gambar Anda
            'instruction': """
            Tugas Anda adalah merespons prediksi siswa tentang output kode `for i in range(5): print(i)` secara ADAPTIF. Jawaban yang benar adalah `0, 1, 2, 3, 4`.

            ALUR WAJIB:
            1.  Analisis jawaban siswa terlebih dahulu.
            
            --> ALUR JIKA JAWABAN SISWA SALAH (misal: '1 2 3 4 5' atau '5'):
                a. JANGAN langsung koreksi. Tanyakan dulu alasan di balik jawabannya. Contoh: "Oke, menarik. Boleh ceritakan, kenapa kamu berpikir outputnya akan seperti itu?"
                b. Setelah siswa memberi alasan, berikan petunjuk yang mengarahkan ke konsep kunci. Contoh: "Terima kasih penjelasannya. Kalau di Python, fungsi `range(5)` itu sebenarnya dimulai dari angka berapa dan berakhir sebelum angka berapa ya?"
                c. Lanjutkan bimbingan hingga siswa menemukan jawaban yang benar, lalu lanjut ke poin 2 di bawah.

            --> ALUR JIKA JAWABAN SISWA BENAR (`0, 1, 2, 3, 4`):
                a. Berikan respons netral yang mengarah ke pendalaman. Contoh: "Menarik! Sekarang, menurutmu kenapa angka terakhir yang muncul adalah 4, bukan 5? Apa alasannya?"
                b. Setelah siswa menjawab, lanjut ke poin 2 di bawah.

            2.  (Minta Prediksi Modifikasi) Setelah alur di atas selesai, tanyakan: "Oke, pemahaman yang bagus. Lalu bagaimana jika kodenya kita ubah menjadi `for i in range(1, 6):`, apa outputnya sekarang?"
            
            3.  Setelah siswa menjawab pertanyaan modifikasi, tutup dengan kalimat: "Baik, prediksimu sudah disimpan. Ayo kita buktikan di tahap berikutnya." dan WAJIB akhiri dengan sinyal [SELESAI].
            """
        },
        
        # Halaman 4 / Step 3: Run, Investigate & Modify
        {
            'step':3,
            'title':'Jalankan Kode Program',
            'type': 'modify_code',
            'is_concludable': True,
            'ct': 'Evaluasi, Inferensi',
            'primm': 'Run, Investigate, Modify',
            'opening_message': "Sekarang giliranmu. Jalankan kode di bawah ini, lalu modifikasi kodenya agar program hanya mencetak angka genap saja (0, 2, 4).",
            'base_code': "for i in range(5):\n    print(f\"Angka ke-{i}\")",
            'instruction': """
            Tugas Anda adalah memandu siswa menjalankan dan memodifikasi kode.
            ALUR WAJIB:
            1. Setelah siswa menjalankan kodenya, tunggu dia melakukan modifikasi.
            2. Setelah siswa berhasil memodifikasi dan mendapatkan jawaban benar (misal dengan menambahkan `if i % 2 == 0:`), tanyakan: "Kerja bagus! Bisakah kamu jelaskan bagaimana caramu menggabungkan logika percabangan di dalam perulangan untuk menyelesaikan masalah ini?"
            3. Setelah siswa menjelaskan, berikan pujian dan tutup dengan: "Penjelasan yang sangat baik! Kamu sudah siap membuat program perulangan sendiri." dan akhiri dengan [SELESAI].
            """
        },
        # Halaman 5 / Step 4: Penjelasan Struktur Kode 'for'
        {
            'step': 4,
            'title': 'Investigasi Kode Program',
            'type': 'socratic_question',
            'is_concludable': True,
            'ct': 'Analisis',
            'opening_message': "Dalam perulangan, ada dua 'resep' utama. Yang pertama adalah `for`. Lihat strukturnya:\n\n"
                            "<pre><code>daftar_buah = ['apel', 'jeruk', 'mangga']\n"
                            "for buah in daftar_buah:\n"
                            "    print(buah)</code></pre>\n"
                            "Bisa jelaskan dengan bahasamu sendiri, apa fungsi dari baris `for buah in daftar_buah:`?",
            'instruction': """
            Tugas Anda adalah memandu siswa memahami anatomi dasar dari loop 'for'.
            ALUR WAJIB:
            1. Setelah siswa menjelaskan, ajukan pertanyaan tentang variabel 'buah'. Tanyakan: "Tepat sekali. Lalu, 'buah' itu variabel apa? Kenapa kita bisa langsung `print(buah)` padahal kita tidak pernah membuat `buah = 'apel'`?"
            2. Setelah siswa menjawab, ajukan pertanyaan tentang indentasi. Tanyakan: "Bagus! Terakhir, kenapa baris `print(buah)` harus menjorok ke dalam?"
            3. Setelah siswa menjawab, tutup dengan kalimat: "Pemahaman yang bagus! Itu adalah dasar dari perulangan `for`. Sekarang mari kita analisis kode yang lain." dan WAJIB akhiri dengan [SELESAI].
            """
        },
        # Halaman 6 / Step 5: Make - Perulangan 'for'
        {
            'step': 5,
            'title':'Membuat Kode Program dengan for',
            'type': 'make_code',
            'is_concludable': True,
            'ct': 'Regulasi Diri',
            'primm': 'Make',
            'opening_message': "Tantangan pertama: Buatlah program dari nol menggunakan perulangan `for`. Studi kasusnya: Kamu punya daftar belanjaan `['roti', 'susu', 'keju']`. Buatlah program yang mencetak setiap barang di daftar tersebut dengan format 'Jangan lupa beli: [nama barang]'.",
            'base_code': "# Tulis kodemu di sini...\n",
            'instruction': """
            Tugas Anda adalah memandu refleksi siswa setelah membuat kode.
            1. Setelah siswa selesai, ajukan pertanyaan reflektif: "Oke. Seberapa yakin kamu kode ini akan tetap berfungsi jika isi daftar belanjaannya kita tambah atau kurangi? Kenapa?"
            2. Setelah siswa menjawab, akhiri dengan: "Poin yang bagus! Itulah kekuatan perulangan `for`. Lanjut ke tantangan berikutnya!" dan sinyal [SELESAI].
            """
        },
        # Halaman 7 / Step 6: Make - Perulangan 'while'
        {
            'step': 6,
            'title':'Membuat Kode Program dengan while',
            'type': 'make_code',
            'is_concludable': True,
            'ct': 'Regulasi Diri',
            'primm': 'Make',
            'opening_message': "Tantangan terakhir: Sekarang gunakan perulangan `while`. Studi kasusnya: Buatlah program hitung mundur dari 5 ke 1, lalu setelah selesai, cetak 'Mulai!'.",
            'base_code': "# Tulis kodemu di sini...\n",
            'instruction': """
            Tugas Anda adalah memandu refleksi siswa setelah membuat kode.
            1. Setelah siswa selesai, ajukan pertanyaan: "Menurutmu, apa yang akan terjadi jika kamu lupa menulis baris kode yang mengurangi nilai variabel hitungan (misal: `hitungan = hitungan - 1`)? Apa nama dari kondisi itu?"
            2. Setelah siswa menjawab (jawaban benar: infinite loop/perulangan tak terbatas), berikan validasi dan pujian, lalu akhiri dengan: "Tepat sekali! Kamu sudah memahami risiko dan cara kerja `while`. Selamat, kamu telah menyelesaikan semua materi perulangan!" dan sinyal [SELESAI].
            """
        }
    ]
    
}

QUIZZES = {
    'algoritma': {
        'title': 'Quiz: Algoritma Pemrograman',
        'questions': [
            {
                'text': 'Apa definisi paling tepat dari algoritma?',
                'options': ['Sebuah bahasa pemrograman', 'Urutan langkah-langkah logis untuk menyelesaikan masalah', 'Sebuah bug dalam kode', 'Nama sebuah software'],
                'correct': 'Urutan langkah-langkah logis untuk menyelesaikan masalah'
            },
            # Tambahkan soal algoritma lainnya di sini...
        ]
    },
    'percabangan': {
        'title': 'Quiz: Struktur Kontrol Percabangan',
        'questions': [
            {
                'text': 'Struktur `if-else` digunakan untuk...',
                'options': ['Mengulang kode berkali-kali', 'Menjalankan kode berdasarkan sebuah kondisi', 'Menyimpan data', 'Menampilkan error'],
                'correct': 'Menjalankan kode berdasarkan sebuah kondisi'
            },
            {
                'text': 'Keyword apa yang digunakan untuk "kondisi lain jika kondisi pertama salah"?',
                'options': ['elif', 'then', 'else', 'when'],
                'correct': 'elif'
            },
            # Tambahkan soal percabangan lainnya di sini...
        ]
    },
    'perulangan': {
        'title': 'Quiz: Struktur Kontrol Perulangan',
        'questions': [
            {
                'text': 'Perulangan `for` paling cocok digunakan untuk...',
                'options': [
                    'Mengulang kode jika sebuah kondisi bernilai True', 
                    'Mengiterasi setiap item dalam sebuah sekuens (seperti list)', 
                    'Membuat keputusan dalam program', 
                    'Menghentikan program saat terjadi error'
                ],
                'correct': 'Mengiterasi setiap item dalam sebuah sekuens (seperti list)'
            },
            {
                'text': 'Apa ciri utama dari perulangan `while`?',
                'options': [
                    'Jumlah perulangannya sudah pasti', 
                    'Akan terus berjalan selama kondisi yang diberikan terpenuhi', 
                    'Hanya berjalan satu kali', 
                    'Selalu digunakan untuk memproses list'
                ],
                'correct': 'Akan terus berjalan selama kondisi yang diberikan terpenuhi'
            },
            {
                'text': 'Kode `for i in range(3):` akan membuat variabel `i` berisi angka apa saja secara berurutan?',
                'options': ['1, 2, 3', '0, 1, 2', '0, 1, 2, 3', 'Hanya angka 3'],
                'correct': '0, 1, 2'
            }
        ]
    }
    # Anda bisa menambahkan materi lain seperti 'perulangan' di sini nanti
}

# Membuat Blueprint 'learning'
learning = Blueprint('learning', __name__, template_folder='templates', static_folder='static')

# app/learning/routes.py

@learning.route('/learning/<module_name>')
def learning_module(module_name):
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    current_user = User.query.filter_by(username=session['username']).first()
    if not current_user:
        return redirect(url_for('auth.logout'))

    # Inisialisasi 'histories' jika belum ada
    if 'histories' not in session:
        session['histories'] = {}
    if module_name not in session['histories']:
        session['histories'][module_name] = {}

    # --- PERBAIKAN: Pindahkan blok ini ke luar 'if' ---
    # Selalu ambil progress MAKSIMAL dari database setiap kali halaman dimuat
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_name=module_name).first()
    max_step_for_this_module = progress.max_step_achieved if progress else 0
    # ----------------------------------------------------

    # Jika user memulai modul baru atau sesi baru
    if session.get('module') != module_name or 'step' not in session:
        session['module'] = module_name
        session['step'] = max_step_for_this_module
        
    current_step_index = session.get('step', 0)
    step_key = str(current_step_index)
    # Cek & buat history untuk step spesifik jika belum ada
    if step_key not in session['histories'][module_name]:
        step_data_for_opening = curriculum[module_name][current_step_index]
        session['histories'][module_name][step_key] = [{'role': 'assistant', 'content': step_data_for_opening.get('opening_message', 'Mari kita mulai.')}]
    # Ambil history yang spesifik untuk MODUL dan STEP saat ini
    chat_history = session['histories'][module_name].get(step_key, [])
    current_step_data = curriculum[module_name][current_step_index]
    
    show_next_button_on_load = False
    if current_step_data.get('is_concludable', False):
        last_message = chat_history[-1]['content'] if chat_history else ''
        if '[SELESAI]' in last_message:
            show_next_button_on_load = True
    
    return render_template('learning.html', 
                             chat_history=chat_history,
                             show_next_button=show_next_button_on_load,
                             step_data=current_step_data,
                             curriculum=curriculum,
                             module_name=module_name,
                             max_step_achieved=max_step_for_this_module)
    
@learning.route('/goto/<module_name>/<int:step_num>')
def goto_step(module_name, step_num):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    # Cek otorisasi (apakah step sudah terbuka)
    current_user = User.query.filter_by(username=session['username']).first()
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_name=module_name).first()
    max_step = progress.max_step_achieved if progress else 0
    if step_num > max_step:
        flash("Anda belum bisa mengakses step tersebut.", "error")
        return redirect(url_for('learning.learning_module', module_name=module_name))

    # HANYA ubah step yang aktif
    session['step'] = step_num
    
    # Arahkan kembali ke learning_module yang akan me-render halaman dengan benar
    return redirect(url_for('learning.learning_module', module_name=module_name))

@learning.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    action = request.json.get('action', 'chat') 
    module_name = session.get('module')
    current_step = session.get('step', 0)
    
    if not module_name or module_name not in curriculum:
        return jsonify({'error': 'Module not found'}), 404
    
    if action == 'next_step':
        next_step_index = current_step + 1
        if next_step_index < len(curriculum[module_name]):
            session['step'] = next_step_index
            
            current_user = User.query.filter_by(username=session['username']).first()
            if current_user:
                # Cari progress user di modul ini
                user_progress = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    module_name=module_name
                ).first()

                # --- PERBAIKAN UTAMA DI SINI ---
                # Jika belum ada progress sama sekali, buat baru sekarang
                if not user_progress:
                    user_progress = UserProgress(
                        user_id=current_user.id,
                        module_name=module_name,
                        max_step_achieved=0 # Mulai dari 0
                    )
                    db.session.add(user_progress)

                # SEKARANG baru aman untuk membandingkan dan update step
                if next_step_index > user_progress.max_step_achieved:
                    user_progress.max_step_achieved = next_step_index
                
                db.session.commit()
            
            return jsonify({'status': 'step_changed'})
        else:
            return jsonify({'status': 'end_of_module'})

    if action == 'run_code':
        modified_code = request.json['message']
        sim_instruction = f"Anda adalah simulator kode Python. Berdasarkan kode berikut, berikan HANYA output programnya, tanpa penjelasan apapun:\n\n{modified_code}"
        try:
            messages = [{"role": "system", "content": sim_instruction}]
            response = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.0)
            output_result = response.choices[0].message.content
            return jsonify({'reply': output_result})
        except Exception as e:
            print(f"Error during code simulation: {e}")
            return jsonify({'reply': 'Gagal mensimulasikan kode.'})
    
    user_input = request.json['message']
    
    # Selalu gunakan string untuk kunci dictionary session
    step_key = str(current_step)

    current_user = User.query.filter_by(username=session['username']).first()
    if current_user:
        log_user = ConversationLog(
            user_id=current_user.id,
            module_name=module_name,
            step_index=current_step,
            role='user',
            content=user_input
        )
        db.session.add(log_user)
        db.session.commit()
    
    step_data = curriculum[module_name][current_step]
    
    # Ambil history dari session menggunakan kunci string
    history = session['histories'][module_name].get(step_key, [])
    
    from prompts import SYSTEM_PROMPT
    task_instruction = step_data.get('instruction', '')

    formatted_system_prompt = SYSTEM_PROMPT.format(task_instruction=task_instruction)
    messages_for_api = [{"role": "system", "content": formatted_system_prompt}] + history
    messages_for_api.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages_for_api, temperature=0.7)
        ai_response = response.choices[0].message.content

        if current_user:
            log_assistant = ConversationLog(
                user_id=current_user.id,
                module_name=module_name,
                step_index=current_step,
                role='assistant',
                content=ai_response
            )
            db.session.add(log_assistant)
            db.session.commit()

        show_next_button = False
        next_action_url = None
        ai_reply_cleaned = ai_response # Buat variabel baru untuk balasan yang sudah bersih

        if step_data.get('is_concludable', False) and '[SELESAI]' in ai_response:
            show_next_button = True
            ai_reply_cleaned = ai_response.replace('[SELESAI]', '').strip()
            
            last_step_index = len(curriculum[module_name]) - 1
            if current_step == last_step_index:
                next_action_url = url_for('learning.quiz', module_name=module_name)
        
        # Tambahkan percakapan baru ke history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": ai_response}) # Simpan respons mentah ke history
        
        # Simpan kembali history ke session menggunakan kunci string
        session['histories'][module_name][step_key] = history
        session.modified = True
        
        return jsonify({
            'reply': ai_reply_cleaned, 
            'show_next_button': show_next_button,
            'next_action_url': next_action_url
        })
    
    except Exception as e:
        print(f"Error calling API: {e}")
        return jsonify({'error': 'Failed to get response from AI'}), 500

@learning.route('/overview/<module_name>')
def module_overview(module_name):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    # Ambil data kurikulum untuk modul yang dipilih
    module_data = curriculum.get(module_name)
    if not module_data:
        # Jika modul tidak ditemukan, kembali ke halaman materi
        flash("Materi tidak ditemukan.", "error")
        return redirect(url_for('main.materi'))

    # Kirim nama modul dan data kurikulumnya ke template baru
    return render_template('module_overview.html', module_name=module_name, module_data=module_data)

@learning.route('/quiz/<module_name>')
def quiz(module_name):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('auth.logout'))

    existing_attempt = QuizAttempt.query.filter_by(
        user_id=user.id,
        module_name=module_name
    ).first()

    if existing_attempt:
        # Jika kuis sudah dikerjakan, buat judul halaman riwayat
        page_title = f"Skor Kuis: {module_name.capitalize()}"
        return render_template('quiz.html', 
                                 module_name=module_name, 
                                 attempt_history=existing_attempt,
                                 quiz_taken=True,
                                 page_title=page_title)

    quiz_data = QUIZZES.get(module_name)
    if not quiz_data:
        flash(f'Quiz untuk materi "{module_name}" belum tersedia.', 'error')
        return redirect(url_for('main.materi'))

    # Jika kuis belum dikerjakan, gunakan judul dari data kuis
    page_title = quiz_data['title']
    correct_answers = [q['correct'] for q in quiz_data['questions']]
    
    return render_template('quiz.html', 
                             quiz_data=quiz_data, 
                             module_name=module_name, 
                             correct_answers=correct_answers,
                             quiz_taken=False,
                             page_title=page_title)

# app/learning/routes.py

@learning.route('/save_quiz_attempt', methods=['POST'])
def save_quiz_attempt():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    user = User.query.filter_by(username=session['username']).first()
    
    if user:
        # Simpan riwayat attempt dan jawaban (kode ini tidak berubah)
        new_attempt = QuizAttempt(...)
        db.session.add(new_attempt)
        db.session.flush()
        for answer_data in data['answers']:
            new_answer = QuizAnswer(...)
            db.session.add(new_answer)
        
        # Logika Sederhana: Tandai modul ini sebagai selesai jika skor > 60
        score = int(data['score'])
        if score >=50:
            progress = UserProgress.query.filter_by(user_id=user.id, module_name=data['module_name']).first()
            if not progress:
                progress = UserProgress(user_id=user.id, module_name=data['module_name'])
                db.session.add(progress)
            progress.is_completed = True

        db.session.commit()
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'User not found'}), 404

    
@learning.route('/quiz/review/<int:attempt_id>')
def quiz_review(attempt_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()

    # 1. Cari attempt kuis berdasarkan ID DAN pastikan itu milik user yang login
    attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=user.id).first_or_404()

    # 2. Kirim objek 'attempt' (yang sudah berisi semua jawabannya) ke template
    return render_template('quiz_review.html', attempt=attempt)
    
@learning.route('/dev-jump/<module_name>/<int:step_num>')
def dev_jump(module_name, step_num):
    # Fungsi ini hanya boleh berjalan dalam mode debug
    if not current_app.debug:
        return "Shortcut is disabled in production mode.", 404
    
    # Pastikan user sudah login
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Logika yang benar: HANYA ubah step dan modul di session
    # JANGAN ubah session['username']
    session['module'] = module_name
    session['step'] = step_num
    session['stage_index'] = 0

    # Reset history chat agar sesuai dengan step yang dituju
    target_step_data = curriculum[module_name][step_num]
    initial_message = target_step_data.get('opening_message', f'Memulai di step {step_num}.')
    session['history'] = [{'role': 'assistant', 'content': initial_message}]

    return redirect(url_for('learning.learning_module', module_name=module_name))

@learning.route('/clear_step_history', methods=['POST'])
def clear_step_history():
    if 'username' not in session:
        return jsonify({'status': 'error'}), 401
    
    data = request.json
    module_name = data.get('module_name')
    # JANGAN ubah ke integer, biarkan sebagai string
    step_index = str(data.get('step_index'))

    if module_name and step_index in session.get('histories', {}).get(module_name, {}):
        del session['histories'][module_name][step_index]
        session.modified = True

    return jsonify({'status': 'success'})