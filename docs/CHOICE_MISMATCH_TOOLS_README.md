# Choice Mismatch Tools - Complete Guide

## 📋 Overview

Koleksi tools lengkap untuk mendeteksi dan memperbaiki masalah mismatch antara pertanyaan dan opsi jawaban.

## 🎯 Masalah yang Diatasi

1. **Gap Fill Questions**: Opsi berupa kalimat lengkap (seharusnya 1-3 kata)
2. **Transformation Questions**: Opsi hanya verb form (seharusnya kalimat lengkap)

## 🛠️ Tools yang Tersedia

### 1. Master Tool (Recommended)
**`master_fix_tool.py`** - Tool utama untuk deteksi dan auto-fix

```bash
# Check saja (tidak fix)
python master_fix_tool.py --check

# Check dan auto-fix
python master_fix_tool.py --fix

# Check dan save report
python master_fix_tool.py --check --report report.json
```

**Fitur:**
- ✅ Deteksi otomatis semua masalah
- ✅ Saran perbaikan untuk setiap masalah
- ✅ Auto-fix untuk masalah yang bisa diperbaiki otomatis
- ✅ Report lengkap dalam JSON

### 2. Fix Specific Question
**`fix_specific_question.py`** - Fix pertanyaan spesifik by ID

```bash
# Lihat pertanyaan
python fix_specific_question.py q_passive_005

# Fix opsi tertentu
python fix_specific_question.py q_passive_005 a "has been"
```

### 3. Comprehensive Check
**`comprehensive_choice_check.py`** - Validasi komprehensif

```bash
python comprehensive_choice_check.py
```

### 4. Review Manual
**`review_gap_fill_and_transformations.py`** - Review semua pertanyaan

```bash
python review_gap_fill_and_transformations.py
```

### 5. Validation
**`validate_and_fix_choices.py`** - Validator dengan deteksi masalah

```bash
python validate_and_fix_choices.py
```

## 📊 Hasil Pemeriksaan

**Status**: ✅ **Tidak ada masalah ditemukan di file JSON**

- Total pertanyaan: **208**
- Gap fill questions: **73** (semua benar ✅)
- Transformation questions: **16** (semua benar ✅)
- Multiple choice questions: **119** (semua benar ✅)

## 🚀 Quick Start

### Step 1: Check Semua Pertanyaan
```bash
python master_fix_tool.py --check
```

### Step 2: Jika Ada Masalah, Auto-Fix
```bash
python master_fix_tool.py --fix
```

### Step 3: Review Hasil
```bash
python review_gap_fill_and_transformations.py
```

## 📝 Contoh Penggunaan

### Contoh 1: Fix Gap Fill dengan Opsi Kalimat Lengkap

**Masalah:**
```
Question ID: q_passive_XXX
Prompt: "Fill in the blank: 'The city _____ built next year.'"
Choice a: "a new city has been built" (SALAH)
```

**Solusi:**
```bash
python fix_specific_question.py q_passive_XXX a "has been"
```

### Contoh 2: Fix Transformation dengan Opsi Verb Form

**Masalah:**
```
Question ID: q_transformation_XXX
Prompt: "Convert to passive voice: 'The teacher explained the lesson.'"
Choice a: "is" (SALAH)
```

**Solusi:**
```bash
python fix_specific_question.py q_transformation_XXX a "The lesson is explained by the teacher."
```

## 📋 Format yang Benar

### Gap Fill Questions ✅
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

**Aturan:**
- Opsi harus **1-3 kata/frasa**
- Bukan kalimat lengkap
- Tidak dimulai dengan artikel (kecuali frasa umum seperti "a lot")

### Transformation Questions ✅
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

**Aturan:**
- Opsi harus **kalimat lengkap** (4+ kata)
- Bukan hanya verb form
- Menunjukkan transformasi yang diminta

## 🔍 Troubleshooting

### Jika Masalah Masih Terjadi di Aplikasi

1. **Clear Database**
   - Hapus database lama di aplikasi
   - Reload data dari JSON files

2. **Rebuild App**
   - Pastikan menggunakan data terbaru
   - Clear cache

3. **Check Database vs JSON**
   - Pastikan database sync dengan JSON files
   - Gunakan `validate_database_sync.py` untuk check

### Jika Question ID Tidak Ditemukan

1. Cek apakah Question ID benar
2. Jalankan `review_gap_fill_and_transformations.py` untuk melihat semua ID
3. Cek di file JSON langsung: `assets/data/question_bank*.json`

## 📚 Dokumentasi Lengkap

- `QUICK_FIX_GUIDE.md` - Quick reference
- `FIX_SUMMARY.md` - Ringkasan hasil pemeriksaan
- `CHOICE_MISMATCH_FIX_GUIDE.md` - Panduan lengkap
- `FINAL_SUMMARY.md` - Ringkasan akhir

## ✅ Checklist

- [x] Tools untuk deteksi masalah
- [x] Tools untuk fix otomatis
- [x] Tools untuk fix manual
- [x] Validasi komprehensif
- [x] Dokumentasi lengkap
- [x] Contoh penggunaan
- [x] Troubleshooting guide

## 🎯 Next Steps

1. ✅ **Identifikasi** Question ID yang bermasalah di aplikasi
2. ✅ **Gunakan tools** untuk melihat/memperbaiki
3. ✅ **Reload data** di aplikasi
4. ✅ **Test ulang** untuk memastikan masalah teratasi

## 💡 Tips

- Gunakan `master_fix_tool.py` untuk check dan fix otomatis
- Gunakan `fix_specific_question.py` untuk fix pertanyaan spesifik
- Semua file JSON sudah benar - tidak perlu diubah kecuali ada masalah spesifik
- Pastikan aplikasi menggunakan data terbaru dari JSON files

---

**Status**: ✅ Semua tools siap digunakan
**File JSON**: ✅ Semua sudah benar (208 pertanyaan)
**Action**: Identifikasi Question ID spesifik jika masih ada masalah

