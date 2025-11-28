# Dokter Grammar

**Aplikasi Pembelajaran Grammar Bahasa Inggris Offline untuk Android**

Dokter Grammar adalah aplikasi Android yang sepenuhnya offline yang dirancang untuk membantu mahasiswa sastra Inggris mengidentifikasi kelemahan grammar, menerima penilaian level, dan mengakses latihan custom adaptif yang disesuaikan dengan kebutuhan mereka.

Tentang Aplikasi

Dokter Grammar adalah aplikasi pembelajaran grammar bahasa Inggris yang menggunakan teknologi adaptif untuk memberikan pengalaman belajar yang personal. Aplikasi ini bekerja sepenuhnya offline, tidak memerlukan koneksi internet, dan semua data disimpan secara lokal di perangkat.

Tujuan Aplikasi

1. **Identifikasi Kelemahan**: Membantu user mengidentifikasi area grammar yang paling lemah
2. **Penilaian Level**: Menentukan level grammar user melalui placement test
3. **Latihan Adaptif**: Memberikan latihan yang disesuaikan dengan kelemahan user
4. **Tracking Progress**: Memantau kemajuan belajar secara visual dan detail
5. **Gamifikasi**: Meningkatkan motivasi melalui badges, streaks, dan achievements

Fitur Utama

1. Placement Test (Tes Penempatan)
- **50 pertanyaan** untuk menentukan level grammar user
- Menilai kemampuan di semua topik grammar
- Menghasilkan skor dan rekomendasi level (Beginner, Intermediate, Advanced)
- Menyediakan penjelasan untuk setiap jawaban
- **Satu kali** dilakukan saat pertama kali menggunakan aplikasi

2. Custom Test (Tes Custom)
- **Latihan adaptif** yang fokus pada area terlemah user
- **Distribusi pertanyaan**:
  - 50% dari topik terlemah
  - 30% dari topik sedang
  - 20% dari topik kuat
- User hanya perlu **memilih jumlah soal** (10, 15, 20, 25, atau 30)
- **Topik dipilih otomatis** oleh engine berdasarkan analisis performa user
- Cocok untuk latihan rutin dan fokus perbaikan

3. Daily Test (Tes Harian)
- **5 pertanyaan cepat** untuk latihan harian
- 40% dari area lemah, 60% random
- Membantu menjaga konsistensi belajar
- Meningkatkan streak harian

4. Reassessment (Re-Assessment)
- **Tes ulang** untuk mengukur kemajuan
- Dua mode:
  - **Targeted**: Fokus pada area lemah
  - **Full**: Tes lengkap seperti placement test
- Digunakan untuk naik level atau mengukur progress

5. Progress Tracking (Pelacakan Kemajuan)
- **Dashboard visual** dengan charts dan grafik
- **Analisis per topik**: Performa detail untuk setiap topik grammar
- **Statistik lengkap**: Total test, akurasi, streak, badges
- **Visualisasi kemajuan**: Grafik line chart untuk tracking progress
- **Topic breakdown**: Pie chart distribusi topik

6. Explanation System (Sistem Penjelasan)
- **Penjelasan untuk setiap pertanyaan** setelah menjawab
- **Rule-based explanations**: Penjelasan berdasarkan aturan grammar
- **AI-powered feedback**: Feedback cerdas menggunakan DialogGPT model
- **Contoh kalimat**: Contoh penggunaan yang benar
- **Tips belajar**: Saran untuk meningkatkan pemahaman

7. Gamification (Gamifikasi)
- **Badge System**: 
  - Streak badges (7, 30, 100 hari)
  - Level badges (intermediate, advanced)
  - Test completion badges (10, 50 test)
  - Topic mastery badges (3, 5 topik)
- **Streak Tracking**: 
  - Tracking latihan harian
  - Perhitungan streak otomatis
  - Reset streak jika melewatkan hari
- **Achievements**: Pencapaian otomatis untuk milestone

8. Backup & Restore
- **Export data**: Ekspor semua data user ke file JSON
- **Import data**: Restore data dari backup
- **File management**: List dan hapus backup
- **Timestamp**: Setiap backup memiliki timestamp

9. Settings (Pengaturan)
- **Profile management**: Edit profil user
- **App configuration**: Konfigurasi aplikasi
- **Data management**: Kelola data dan backup

Arsitektur Teknis

### Tech Stack
- **Framework**: Flutter (Dart) - Cross-platform framework
- **Database**: SQLite (sqflite) - Local database
- **State Management**: Provider - State management pattern
- **Charts**: fl_chart - Library untuk visualisasi data
- **AI/ML**: On-device AI model untuk feedback adaptif

### Struktur Project
```
lib/
├── core/                    # Core functionality
│   ├── constants/          # App constants, colors, strings
│   ├── database/           # Database schema dan helper
│   ├── models/             # Data models (Question, User, dll)
│   └── services/           # Business logic services
│       ├── adaptive_algorithm.dart    # Algoritma adaptif
│       ├── scoring_service.dart       # Scoring logic
│       ├── explanation_service.dart   # Explanation generation
│       └── ai_service.dart            # AI service
├── data/                   # Data layer
│   ├── datasources/        # Local data sources
│   │   ├── local/          # SQLite data source
│   │   └── assets/         # JSON data source
│   └── repositories/       # Data repositories
└── presentation/           # UI layer
    ├── screens/            # App screens
    │   ├── home/           # Home screen
    │   ├── test/           # Test screen
    │   ├── progress/       # Progress screen
    │   ├── custom_test/    # Custom test config
    │   └── settings/       # Settings screen
    ├── widgets/            # Reusable widgets
    └── theme/              # App theme
```

Memulai Penggunaan

### Prerequisites (Persyaratan)
- **Flutter SDK**: Versi 3.7.0 atau lebih tinggi
- **Android Studio** atau **VS Code** dengan Flutter extension
- **Android device** atau **emulator** (Android 5.0+)
- **Git** (untuk clone repository)

Installation (Instalasi)

1. **Clone repository**:
```bash
git clone <repository-url>
cd dokter_grammar2
```

2. **Install dependencies**:
```bash
flutter pub get
```

3. **Run aplikasi**:
```bash
flutter run
```

First Run introduction (Penggunaan Pertama)

1. **Onboarding**:
   - Masukkan nickname
   - Pilih tujuan belajar
   - Pilih minat (interests)

2. **Placement Test**:
   - Selesaikan 50 pertanyaan
   - Review hasil dan penjelasan
   - Terima rekomendasi level

3. **Mulai Latihan**:
   - Gunakan Custom Test untuk latihan fokus
   - Gunakan Daily Test untuk latihan harian
   - Pantau progress di Progress screen

Database Schema

Aplikasi menggunakan SQLite dengan tabel-tabel berikut:

### Tabel Utama

1. **users**
   - Menyimpan profil user
   - Fields: id, nickname, goal, interests, level, created_at

2. **questions**
   - Bank pertanyaan
   - Fields: id, type, difficulty, topic_id, prompt, answer, choices, tags

3. **topics**
   - Topik grammar
   - Fields: id, name, display_name

4. **test_sessions**
   - Sesi test
   - Fields: id, user_id, session_type, total_questions, score, started_at, completed_at

5. **test_attempts**
   - Jawaban individual
   - Fields: id, session_id, question_id, user_answer, is_correct

6. **user_topic_performance**
   - Performa per topik
   - Fields: user_id, topic_id, total_attempts, correct_attempts, mastery_level

7. **badges**
   - Badge yang diperoleh
   - Fields: id, user_id, badge_type, badge_name, earned_at

8. **daily_activities**
   - Tracking aktivitas harian
   - Fields: id, user_id, activity_date, test_count, streak

Design System

### Color Scheme (Skema Warna)
- **Primary**: Lemon gradient (soft pastel) - #FFF9C4
- **Primary Light**: Light lemon - #FFFDE7
- **Secondary**: Orange accents
- **Text Primary**: Dark colors untuk readability
- **Text Secondary**: Gray untuk secondary text
- **Background**: White
- **Card Background**: White dengan shadow
- **Error**: Red untuk error messages
- **Success**: Green untuk success messages

UI Components
- **Material Design 3**: Mengikuti Material Design guidelines
- **Custom Gradients**: Gradient cards untuk visual appeal
- **Responsive Layouts**: Layout yang responsif untuk berbagai ukuran layar
- **Accessible Colors**: Kontras warna yang baik untuk accessibility
- **Modern Header**: Header dengan back button dan title
- **Card Design**: Cards dengan shadow dan border radius

Adaptive Algorithm (Algoritma Adaptif)

Aplikasi menggunakan algoritma adaptif cerdas untuk pemilihan pertanyaan:

### Custom Test Algorithm
- **50%** dari topik terlemah (weakest topics)
- **30%** dari topik sedang (medium topics)
- **20%** dari topik kuat (strong topics)
- Berdasarkan analisis performa user di setiap topik

### Daily Test Algorithm
- **40%** dari area lemah
- **60%** random dari semua topik
- Untuk menjaga variasi dan fokus perbaikan

### Reassessment Algorithm
- **Targeted Mode**: Fokus pada area lemah saja
- **Full Mode**: Distribusi seperti placement test

### Mastery Calculation
- Mastery level dihitung berdasarkan:
  - Total attempts per topik
  - Correct attempts per topik
  - Recent performance (weighted)
- Formula: `mastery = (correct_attempts / total_attempts) * 100`

Gamification System

### Badge Types (Jenis Badge)

1. **Streak Badges**
   - 7 hari streak
   - 30 hari streak
   - 100 hari streak

2. **Level Badges**
   - Intermediate level
   - Advanced level

3. **Test Completion Badges**
   - 10 test completed
   - 50 test completed
   - 100 test completed

4. **Topic Mastery Badges**
   - 3 topik dikuasai
   - 5 topik dikuasai
   - 10 topik dikuasai

Streak System
- **Daily tracking**: Mencatat latihan harian
- **Automatic calculation**: Perhitungan streak otomatis
- **Reset mechanism**: Streak reset jika melewatkan hari
- **Visual indicator**: Indikator visual di home screen

Konten Grammar

Aplikasi mencakup **12 topik grammar utama**:

1. **Tenses** (Bentuk Waktu)
   - Simple present, past, future
   - Present/past continuous
   - Present/past perfect
   - Future perfect, dll

2. **Modals & Auxiliaries** (Modal & Kata Bantu)
   - Can, could, should, must
   - May, might, will, would
   - Have to, need to, dll

3. **Conditionals** (Kalimat Pengandaian)
   - First, second, third conditional
   - Mixed conditional

4. **Complex Sentences** (Kalimat Kompleks)
   - Subordinate clauses
   - Relative clauses

5. **Sentence Combining & Punctuation** (Penggabungan Kalimat & Tanda Baca)
   - Combining sentences
   - Punctuation rules

6. **Articles & Determiners** (Artikel & Determiner)
   - A, an, the
   - Determiners

7. **Subject-Verb Agreement** (Kesepakatan Subjek-Kata Kerja)
   - Singular/plural agreement
   - Special cases

8. **Passive Voice** (Kalimat Pasif)
   - Active to passive transformation
   - Passive forms

9. **Reported Speech** (Kalimat Tidak Langsung)
   - Direct to indirect speech
   - Tense changes

10. **Prepositions** (Kata Depan)
    - Place, time, direction
    - Common prepositions

11. **Adjective Clauses** (Klausa Kata Sifat)
    - Relative clauses
    - Which, that, who, where, when

12. **Pronouns & Reference** (Kata Ganti & Referensi)
    - Personal, possessive, reflexive pronouns
    - Pronoun reference

### Question Bank
- **Total**: 208+ pertanyaan
- **Types**: Multiple choice, gap fill, sentence transformation
- **Difficulty**: Level 1-5
- **Coverage**: Semua topik grammar

## 🔒 Privacy & Security

### Privacy Features
- **100% Offline**: Tidak memerlukan koneksi internet
- **Local Storage**: Semua data disimpan di perangkat
- **No Analytics**: Tidak ada pengumpulan data
- **No Tracking**: Tidak ada tracking user behavior
- **User Control**: User memiliki kontrol penuh atas data

Data Security
- **SQLite Encryption**: Database terlindungi
- **Local Files**: Backup files disimpan lokal
- **No Cloud Sync**: Tidak ada sinkronisasi cloud
- **User Privacy**: Data user tetap private

Backup & Restore

### Export Data
- **Format**: JSON file
- **Content**: Semua data user (profile, test sessions, progress, badges)
- **Timestamp**: Setiap backup memiliki timestamp
- **Location**: Disimpan di local storage

### Import Data
- **Restore**: Restore semua data dari backup
- **Validation**: Validasi data sebelum import
- **Merge**: Opsi untuk merge atau replace data

### File Management
- **List Backups**: Lihat semua backup yang tersedia
- **Delete Backup**: Hapus backup yang tidak diperlukan
- **View Details**: Lihat detail setiap backup

Development

### Running Tests
```bash
flutter test
```

### Building APK
```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release

# Split APK (untuk ukuran lebih kecil)
flutter build apk --split-per-abi --release
```

### Code Structure
- **Clean Architecture**: Mengikuti clean architecture pattern
- **Separation of Concerns**: Pemisahan yang jelas antara layers
- **Repository Pattern**: Pattern untuk data access
- **Provider Pattern**: State management dengan Provider
- **Best Practices**: Mengikuti Flutter best practices

### Development Tools
- **Linter**: Analysis options untuk code quality
- **Formatting**: Dart formatter untuk konsistensi
- **Testing**: Unit tests dan widget tests
- **Debugging**: Debug tools dan logging

## 🤖 Model AI DialogGPT untuk Penjelasan Grammar

### Apa Itu Model AI Ini?

Aplikasi Dokter Grammar menggunakan **Model AI DialogGPT** yang telah dilatih khusus untuk menghasilkan penjelasan grammar yang natural dan mudah dipahami. Model ini menggunakan teknologi **Deep Learning (Pembelajaran Mendalam)** berbasis **GPT-2** yang di-fine-tune dengan dataset grammar questions dari aplikasi ini.

### Tujuan Model

Model AI ini dirancang untuk:

1. **Menghasilkan Penjelasan yang Natural**
   - Penjelasan tidak lagi kaku seperti template
   - Bahasa lebih natural dan mudah dipahami
   - Dapat menyesuaikan dengan konteks pertanyaan

2. **Memberikan Penjelasan yang Kontekstual**
   - Memahami grammar point yang ditanyakan (simple present, past tense, dll)
   - Menyesuaikan penjelasan dengan jawaban user (benar/salah)
   - Memberikan contoh yang relevan dengan konteks

3. **Meningkatkan Pengalaman Belajar**
   - Penjelasan lebih personal dan mudah dipahami
   - Dapat menjelaskan kesalahan dengan detail
   - Memberikan insight yang lebih dalam tentang grammar

### Bagaimana Model Bekerja?

#### 1. Arsitektur Model

Model menggunakan **GPT-2 Small** (117 juta parameter) sebagai base model, yang kemudian di-fine-tune menggunakan dataset grammar questions dari aplikasi.

**Komponen Utama:**
- **Transformer Architecture**: Menggunakan attention mechanism untuk memahami konteks
- **Language Model**: Dapat menghasilkan teks secara otomatis
- **Fine-tuned**: Disesuaikan khusus untuk domain grammar English

#### 2. Proses Training

**Data Training:**
- **665 contoh training** dari question bank aplikasi
- **167 contoh validation** untuk evaluasi
- Setiap contoh berisi: pertanyaan, jawaban user, jawaban benar, dan penjelasan

**Hasil Training:**
- **Loss Awal**: 3.8251 (tinggi, model belum belajar)
- **Loss Akhir**: 0.37 (rendah, model sudah belajar dengan baik)
- **Evaluation Loss**: 0.33 (model performa baik pada data baru)
- **Epochs**: 3 putaran training

#### 3. Cara Model Menghasilkan Penjelasan

**Input yang Diterima Model:**
```
Question: "Choose the correct form: 'I _____ to school every day.'"
Type: multiple_choice
Grammar Point: simple_present
User Answer: "went"
Correct Answer: "go"
Is Correct: False
```

**Proses Generasi:**
1. **Tokenization**: Input diubah menjadi tokens (kata-kata yang dipahami model)
2. **Context Understanding**: Model memahami konteks pertanyaan
3. **Generation**: Model menghasilkan penjelasan kata demi kata
4. **Decoding**: Tokens diubah kembali menjadi teks yang bisa dibaca

**Output yang Dihasilkan:**
```
"Use simple present for actions that started in the past and continue to the present. 
Contoh yang benar: I go to school every day."
```

### Cara Menggunakan Model

Aplikasi menggunakan model dalam dua cara:

#### Opsi 1: Pre-Generated JSON (Saat Ini Digunakan) ✅

**Cara Kerja:**
- Model digunakan untuk generate penjelasan untuk semua pertanyaan sekali
- Penjelasan disimpan dalam file JSON (`assets/data/ai_explanations.json`)
- Aplikasi membaca dari JSON (instant, tidak perlu model di runtime)

**Keuntungan:**
- ✅ Sangat cepat (instant lookup)
- ✅ Tidak perlu server atau model di device
- ✅ Bekerja offline sepenuhnya
- ✅ Tidak perlu load model (hemat memori)

**File yang Digunakan:**
- `assets/data/ai_explanations.json` - Berisi semua penjelasan yang sudah di-generate

#### Opsi 2: Python Server (Untuk Development/Testing)

**Cara Kerja:**
- Jalankan server Python yang memuat model
- Aplikasi memanggil server via HTTP
- Server menghasilkan penjelasan menggunakan model langsung
- Penjelasan dikembalikan ke aplikasi

**Keuntungan:**
- ✅ Menggunakan model langsung (dinamis)
- ✅ Dapat menyesuaikan dengan konteks real-time
- ✅ Penjelasan selalu fresh

**Cara Menjalankan:**
```bash
python scripts/ai_explanation_server.py
```

### Perbedaan dengan Sistem Lama

#### Sistem Lama (Template-Based)

**Cara Kerja:**
- Menggunakan template yang sudah ditentukan
- Penjelasan statis dan kaku
- Tidak bisa menyesuaikan dengan konteks

**Keterbatasan:**
- ❌ Penjelasan kurang natural
- ❌ Tidak bisa menjelaskan kesalahan secara detail
- ❌ Harus membuat template untuk setiap kasus

#### Sistem Baru (AI Model)

**Cara Kerja:**
- Model memahami konteks pertanyaan
- Menghasilkan penjelasan secara dinamis
- Dapat menyesuaikan dengan berbagai situasi

**Keuntungan:**
- ✅ Penjelasan lebih natural
- ✅ Dapat menjelaskan kesalahan dengan detail
- ✅ Tidak perlu membuat template untuk setiap kasus
- ✅ Dapat belajar dan berkembang

### Contoh Penggunaan Model

#### Contoh 1: Pertanyaan Simple Present

**Input:**
- Question: "Choose the correct form: 'I _____ to school every day.'"
- User Answer: "went" (salah)
- Correct Answer: "go"
- Grammar Point: "simple_present"

**Output Model:**
```
"Use simple present for actions that started in the past and continue to the present. 
Contoh yang benar: I go to school every day."
```

#### Contoh 2: Pertanyaan Past Tense

**Input:**
- Question: "What did you do yesterday?"
- User Answer: "go" (salah)
- Correct Answer: "went"
- Grammar Point: "simple_past"

**Output Model:**
```
"Use simple past tense for completed actions in the past. 
'Go' is present tense. The correct form is 'went' for past tense. 
Contoh yang benar: I went to the store yesterday."
```

### Lokasi Model

Model yang telah dilatih tersimpan di:
```
models/dialogpt_grammar/
├── config.json              # Konfigurasi model
├── model.safetensors        # Bobot model (~45-50 MB)
├── tokenizer_config.json    # Konfigurasi tokenizer
├── vocab.json               # Vocabulary (kamus kata)
├── merges.txt               # BPE merges (untuk tokenization)
└── generation_config.json   # Konfigurasi generation
```

**Ukuran Total**: ~45-50 MB

### Dokumentasi Lengkap

Untuk penjelasan lebih detail tentang model AI, lihat:
- **[MODEL_AI_PENJELASAN.md](docs/MODEL_AI_PENJELASAN.md)** - Penjelasan lengkap dalam Bahasa Indonesia
- **[TRAINED_MODEL_USAGE_GUIDE.md](docs/TRAINED_MODEL_USAGE_GUIDE.md)** - Panduan penggunaan model
- **[TRAINING_COMPLETE.md](docs/TRAINING_COMPLETE.md)** - Hasil training model

---

## 📝 Development Status

**Progress Saat Ini: 95%**

### Completed Features ✅
- ✅ Placement Test
- ✅ Custom Test dengan adaptive algorithm
- ✅ Daily Test
- ✅ Reassessment
- ✅ Progress Tracking dengan charts
- ✅ Explanation System
- ✅ Badge System
- ✅ Streak Tracking
- ✅ Backup & Restore
- ✅ Settings
- ✅ Onboarding
- ✅ UI/UX Design

### In Progress 🚧
- 🚧 AI Model ONNX Integration (on-device) - Model sudah trained, tinggal export
- 🚧 Advanced Analytics
- 🚧 More Badge Types

Lihat [STATUS.md](STATUS.md) untuk detail progress development dan version history.

 Documentation

 Dokumentasi Lengkap
- **STATUS.md**: Status development dan version history
- **TESTING_GUIDE.md**: Panduan testing aplikasi
- **ARCHITECTURE_COMPLIANCE.md**: Arsitektur dan compliance
- **ANDROID_DEPLOYMENT_SOLUTIONS.md**: Solusi deployment Android

Dokumentasi AI Model
- **MODEL_AI_PENJELASAN.md**: Penjelasan lengkap model AI dalam Bahasa Indonesia
- **TRAINED_MODEL_USAGE_GUIDE.md**: Panduan penggunaan model AI
- **TRAINING_COMPLETE.md**: Hasil training model
- **DIALOGPT_TRAINING_PROPOSAL.md**: Proposal training model

Documentation
- **CHOICE_MISMATCH_TOOLS_README.md**: Tools untuk fix mismatch pertanyaan
- **QUICK_FIX_GUIDE.md**: Quick reference untuk fix issues



## 🤝 Contributing

Ini adalah project private versi ke 2 untuk hackathon pertama kami.

## 📄 License

*Informasi license akan ditambahkan*

## 🙏 Acknowledgments

- **Flutter Team**: Untuk framework yang luar biasa
- **SQLite**: Untuk local storage yang reliable
- **Community**: Untuk semua kontributor dan tester
- **Open Source Libraries**: Untuk semua library yang digunakan


### Version 1.0 (Current)
- ✅ Core features
- ✅ Adaptive algorithm
- ✅ Progress tracking
- ✅ Gamification

### Version 1.1 (Planned)
- 📋 Enhanced AI feedback
- 📋 More question types
- 📋 Advanced analytics

### Version 2.0 (Future)
- 📋 Social features
- 📋 Study groups
- 📋 Cloud sync (optional)


**Version**: 0.1.0  
**Last Updated**: 2024-11-27  
**Status**: MVP Complete, Ready for Testing  
**Language**: Bahasa Indonesia
