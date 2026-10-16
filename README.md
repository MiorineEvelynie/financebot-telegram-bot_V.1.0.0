# FinanceBot Automation

Bot Telegram pencatat keuangan otomatis untuk UMKM. Kirim teks, foto nota, atau voice note — AI akan mengekstrak data transaksi dan menyimpannya ke Google Sheets secara otomatis.

## Fitur

- **Input fleksibel**: teks, foto struk/nota, atau voice note
- **Ekstraksi AI**: Google Gemini mengurai tanggal, kategori, deskripsi, tipe, dan nominal transaksi
- **Simpan otomatis**: data langsung masuk ke Google Sheets, siap dianalisis
- **Retry otomatis**: tahan terhadap gangguan sementara pada server AI (503/429)

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Bot interface | Telegram Bot API (`python-telegram-bot`) |
| AI extraction | Google Gemini (`google-genai`) |
| Database | Google Sheets (`gspread`) |
| Bahasa | Python 3.11+ |

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/USERNAME/financebot-automation.git
cd financebot-automation
pip install -r requirements.txt
```

### 2. Siapkan kredensial

| Kredensial | Didapat dari |
|---|---|
| `TELEGRAM_TOKEN` | [@BotFather](https://t.me/BotFather) di Telegram, perintah `/newbot` |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `service_account.json` | Google Cloud Console → Service Account → buat key JSON |

Share Google Sheets target ke email `client_email` yang ada di dalam `service_account.json`, dengan akses **Editor**.

### 3. Set environment variables

```bash
# Windows PowerShell
$env:TELEGRAM_TOKEN="token_anda"
$env:GEMINI_API_KEY="key_anda"

# Linux/Mac
export TELEGRAM_TOKEN="token_anda"
export GEMINI_API_KEY="key_anda"
```

Letakkan `service_account.json` di folder root project (sejajar dengan `test.py`).

### 4. Siapkan struktur spreadsheet

Buat tab bernama persis **`Data_Mentah`** dengan header baris pertama:

```
ID Transaksi | Tanggal | Kategori | Deskripsi Barang | Tipe | Nominal (Rp) | Catatan | Pengirim
```

Isi `SHEET_ID` di `test.py` dengan ID spreadsheet Anda (bagian URL di antara `/d/` dan `/edit`).

### 5. Jalankan

```bash
python test.py
```

## Deploy 24/7 (Railway)

1. Push repo ini ke GitHub (`service_account.json` otomatis tidak ikut ter-push, lihat `.gitignore`)
2. Buat project baru di [railway.app](https://railway.app), hubungkan ke repo ini
3. Tambahkan environment variables: `TELEGRAM_TOKEN`, `GEMINI_API_KEY`, `GOOGLE_CREDS_JSON` (isi seluruh konten `service_account.json`)
4. Railway otomatis install dependencies dan menjalankan bot

## Status Proyek

Prototipe / MVP — belum ada whitelist atau sistem pembayaran. Semua user yang chat bot akan dilayani dan datanya masuk ke satu spreadsheet yang sama.

## Keamanan

- Jangan commit `service_account.json` atau file `.env` (sudah ada di `.gitignore`)
- Jangan tempel token/API key langsung di kode
- Rotasi token/key secara berkala, terutama jika pernah tidak sengaja terekspos

## Lisensi

Proyek internal — Venture Creation x Web Programming.
