# Panduan Perbaikan Mismatch Pertanyaan dan Opsi

## Masalah yang Dilaporkan

1. **Gap Fill Questions**: Pertanyaan fill-in-the-blank seperti "the city was built next year" tapi opsi jawabannya malah kalimat baru seperti "a new city has been built" (seharusnya opsi seperti "was", "will be", "is", dll)

2. **Sentence Transformation Questions**: Pertanyaan "change this sentence into..." tapi opsi jawabannya hanya bentuk "to be" (is, are, was, were) bukan kalimat yang sudah ditransformasi

## Hasil Pemeriksaan

Setelah memeriksa semua file question bank (question_bank1.json, question_bank2.json, question_bank3.json), **semua pertanyaan di file JSON terlihat benar**:
- ✅ Gap fill questions memiliki opsi 1-3 kata (bukan kalimat lengkap)
- ✅ Transformation questions memiliki opsi kalimat lengkap yang sudah ditransformasi

## Kemungkinan Penyebab

Karena data di JSON sudah benar, masalah mungkin terjadi karena:

1. **Data di Database Berbeda**: Aplikasi mungkin menggunakan database lokal yang berbeda dari file JSON
2. **Bug di Runtime**: Ada bug saat memuat/menampilkan pertanyaan
3. **Cache/Data Lama**: Aplikasi menggunakan data lama yang belum diupdate

## Solusi

### Langkah 1: Identifikasi Pertanyaan Bermasalah

Jalankan script untuk melihat semua pertanyaan:

```bash
python review_gap_fill_and_transformations.py
```

Script ini akan menampilkan semua gap fill dan transformation questions dengan opsi jawabannya.

### Langkah 2: Validasi Data

Jalankan validator untuk memastikan tidak ada masalah:

```bash
python validate_and_fix_choices.py
```

### Langkah 3: Perbaiki Manual

Jika menemukan pertanyaan bermasalah:

1. **Untuk Gap Fill dengan Opsi Kalimat Lengkap**:
   - Buka file JSON yang sesuai (question_bank1.json, question_bank2.json, atau question_bank3.json)
   - Cari pertanyaan berdasarkan ID
   - Ganti opsi kalimat lengkap dengan kata/frasa yang sesuai (1-3 kata)
   - Contoh: Jika opsi "a new city has been built", ganti dengan "has been" atau "will be"

2. **Untuk Transformation dengan Opsi Verb Form**:
   - Buka file JSON yang sesuai
   - Cari pertanyaan berdasarkan ID
   - Ganti opsi verb form dengan kalimat lengkap yang sudah ditransformasi
   - Contoh: Jika opsi hanya "is" atau "was", ganti dengan kalimat lengkap seperti "The sentence is transformed."

### Langkah 4: Update Database (jika menggunakan database)

Jika aplikasi menggunakan database lokal:

1. Hapus database lama
2. Reload data dari file JSON yang sudah diperbaiki
3. Atau update langsung di database dengan query SQL

## Script yang Tersedia

1. **review_gap_fill_and_transformations.py**: Menampilkan semua gap fill dan transformation questions untuk review manual
2. **validate_and_fix_choices.py**: Validator yang memeriksa apakah opsi sesuai dengan tipe pertanyaan
3. **find_choice_mismatches.py**: Script komprehensif untuk menemukan semua mismatch
4. **test_question_answer_mismatch.py**: Test untuk memastikan answer field sesuai dengan choices

## Format yang Benar

### Gap Fill Questions
```json
{
  "type": "gap_fill",
  "prompt": "Fill in the blank: 'The city _____ built next year.'",
  "choices": [
    {"choiceId": "a", "text": "is", "isCorrect": false},
    {"choiceId": "b", "text": "will be", "isCorrect": true},
    {"choiceId": "c", "text": "was", "isCorrect": false},
    {"choiceId": "d", "text": "has been", "isCorrect": false}
  ]
}
```

✅ **Benar**: Opsi adalah kata/frasa (1-3 kata)
❌ **Salah**: Opsi adalah kalimat lengkap seperti "A new city has been built."

### Transformation Questions
```json
{
  "type": "multiple_choice",
  "prompt": "Convert to passive voice: 'The teacher explained the lesson.'",
  "choices": [
    {"choiceId": "a", "text": "The teacher was explained the lesson.", "isCorrect": false},
    {"choiceId": "b", "text": "The lesson was explained by the teacher.", "isCorrect": true},
    {"choiceId": "c", "text": "The lesson is explaining by the teacher.", "isCorrect": false},
    {"choiceId": "d", "text": "The lesson explained by the teacher.", "isCorrect": false}
  ]
}
```

✅ **Benar**: Opsi adalah kalimat lengkap yang sudah ditransformasi
❌ **Salah**: Opsi hanya verb form seperti "is", "are", "was", "were"

## Cara Melaporkan Masalah Spesifik

Jika masih menemukan masalah setelah memeriksa:

1. Catat **Question ID** yang bermasalah
2. Catat **Prompt** pertanyaan
3. Catat **Opsi yang salah** (choiceId dan text)
4. Jelaskan **apa yang seharusnya** menjadi opsi yang benar

Contoh:
```
Question ID: q_passive_XXX
Prompt: "Fill in the blank: 'The city _____ built next year.'"
Masalah: Choice a = "a new city has been built" (seharusnya "has been" atau "will be")
```

## Next Steps

1. ✅ Jalankan `review_gap_fill_and_transformations.py` untuk melihat semua pertanyaan
2. ✅ Identifikasi pertanyaan spesifik yang bermasalah
3. ✅ Perbaiki di file JSON yang sesuai
4. ✅ Reload data di aplikasi
5. ✅ Test ulang untuk memastikan masalah teratasi

