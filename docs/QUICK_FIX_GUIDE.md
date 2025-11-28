# Quick Fix Guide - Mismatch Pertanyaan dan Opsi

## Masalah yang Dilaporkan

1. Gap fill questions memiliki opsi kalimat lengkap (seharusnya 1-3 kata)
2. Transformation questions memiliki opsi hanya verb form (seharusnya kalimat lengkap)

## Cara Menggunakan Tools

### 1. Cari Pertanyaan Spesifik

Jika Anda tahu Question ID yang bermasalah:

```bash
python fix_specific_question.py q_passive_005
```

Ini akan menampilkan pertanyaan dan semua opsi-nya.

### 2. Perbaiki Pertanyaan Spesifik

Jika Anda tahu Question ID dan ingin memperbaiki opsi tertentu:

```bash
python fix_specific_question.py q_passive_005 a "has been"
```

Ini akan mengubah choice "a" menjadi "has been" dan menyimpan ke file JSON.

### 3. Review Semua Pertanyaan

Untuk melihat semua gap fill dan transformation questions:

```bash
python review_gap_fill_and_transformations.py
```

### 4. Validasi Komprehensif

Untuk memeriksa semua pertanyaan:

```bash
python comprehensive_choice_check.py
```

## Contoh Perbaikan

### Contoh 1: Gap Fill dengan Opsi Kalimat Lengkap

**Masalah:**
```
Question ID: q_passive_XXX
Prompt: "Fill in the blank: 'The city _____ built next year.'"
Choice a: "a new city has been built" (SALAH - kalimat lengkap)
```

**Perbaikan:**
```bash
python fix_specific_question.py q_passive_XXX a "has been"
```

Atau manual edit di file JSON:
```json
{
  "choiceId": "a",
  "text": "has been",  // Diubah dari "a new city has been built"
  "isCorrect": false
}
```

### Contoh 2: Transformation dengan Opsi Verb Form

**Masalah:**
```
Question ID: q_transformation_XXX
Prompt: "Convert to passive voice: 'The teacher explained the lesson.'"
Choice a: "is" (SALAH - hanya verb form)
```

**Perbaikan:**
```bash
python fix_specific_question.py q_transformation_XXX a "The lesson is explained by the teacher."
```

Atau manual edit di file JSON:
```json
{
  "choiceId": "a",
  "text": "The lesson is explained by the teacher.",  // Diubah dari "is"
  "isCorrect": false
}
```

## Format yang Benar

### Gap Fill Questions ✅
- Opsi harus **1-3 kata/frasa**
- Contoh: "is", "was", "will be", "has been", "where", "which"

### Transformation Questions ✅
- Opsi harus **kalimat lengkap** (4+ kata)
- Contoh: "The lesson was explained by the teacher."

## Troubleshooting

### Jika Question ID Tidak Ditemukan

1. Cek apakah Question ID benar
2. Jalankan `review_gap_fill_and_transformations.py` untuk melihat semua Question ID
3. Cek di file JSON langsung: `assets/data/question_bank*.json`

### Jika Perbaikan Tidak Tersimpan

1. Pastikan file JSON tidak sedang dibuka di editor lain
2. Cek permission file
3. Coba edit manual di file JSON

### Jika Masalah Masih Terjadi di Aplikasi

1. **Clear database**: Hapus database lama di aplikasi
2. **Reload data**: Pastikan aplikasi memuat data dari JSON terbaru
3. **Rebuild app**: Rebuild aplikasi untuk memastikan data terbaru ter-load

## Next Steps

1. ✅ Identifikasi Question ID yang bermasalah di aplikasi
2. ✅ Gunakan `fix_specific_question.py` untuk melihat pertanyaan
3. ✅ Perbaiki opsi yang salah
4. ✅ Reload data di aplikasi
5. ✅ Test ulang

## Script Reference

| Script | Purpose |
|--------|---------|
| `fix_specific_question.py` | Fix pertanyaan spesifik by ID |
| `review_gap_fill_and_transformations.py` | Review semua gap fill & transformation |
| `comprehensive_choice_check.py` | Validasi komprehensif semua pertanyaan |
| `validate_and_fix_choices.py` | Validator dengan auto-fix suggestions |

## Butuh Bantuan?

Jika masih menemukan masalah:
1. Berikan **Question ID** spesifik
2. Berikan **Prompt** pertanyaan
3. Berikan **Opsi yang salah** (choiceId dan text)
4. Jelaskan **apa yang seharusnya**

Saya akan membantu memperbaikinya!

