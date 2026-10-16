import os, json, time
from datetime import date
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import gspread

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.6-flash"

gc = gspread.service_account(filename="service_account.json")

# Tanpa whitelist / paywall: semua user yang chat bot akan dilayani
# dan datanya masuk ke SATU spreadsheet bersama ini.
SHEET_ID = "1hMkFYor8hM-aR31b0omjgkFYmb8ng1lscEl4_g4Rhww"

# Link untuk perintah /opencsv
# gid=0 = tab pertama. Ganti sesuai gid tab "Data_Mentah" jika berbeda
# (lihat di URL browser saat tab itu dibuka, angka setelah "gid=").
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

PROMPT = """Kamu asisten pencatat keuangan UMKM Indonesia.
Ekstrak transaksi dari input berikut. Balas HANYA JSON valid, tanpa teks lain:
{
  "tanggal": "YYYY-MM-DD",
  "kategori": "string",
  "deskripsi": "string",
  "tipe": "Pemasukan" atau "Pengeluaran",
  "nominal": angka tanpa titik/koma (contoh 35000),
  "catatan": "string"
}
Aturan: "35 ribu"=35000, "1,5 juta"=1500000. Jika tanggal tidak disebut, pakai {today}.
Jika ada beberapa item, balas array JSON."""

def extract(parts):
    prompt = PROMPT.replace("{today}", date.today().isoformat())
    last_err = None
    for attempt in range(4):
        try:
            res = client.models.generate_content(
                model=MODEL,
                contents=[prompt] + parts,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            data = json.loads(res.text)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            last_err = e
            msg = str(e)
            if "503" in msg or "UNAVAILABLE" in msg or "429" in msg:
                time.sleep(2 * (attempt + 1))  # tunggu 2, 4, 6, 8 detik
                continue
            raise
    raise last_err

def write_rows(sheet_id, rows, user_label):
    ws = gc.open_by_key(sheet_id).worksheet("Data_Mentah")
    for r in rows:
        ws.append_row([
            f"TRX-{date.today():%y%m%d}-{len(ws.col_values(1)):04d}",
            r["tanggal"], r["kategori"], r["deskripsi"],
            r["tipe"], r["nominal"], r.get("catatan", ""),
            user_label,  # kolom tambahan: siapa pengirimnya
        ], value_input_option="USER_ENTERED")

async def opencsv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 Data transaksi kamu:\n\n"
        f"Lihat di Sheets: {SHEET_URL}\n\n"
        f"Unduh sebagai CSV: {CSV_URL}"
    )

async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = msg.from_user
    user_label = f"{user.full_name} ({user.id})"

    try:
        if msg.text:
            parts = [msg.text]
        elif msg.photo:
            f = await msg.photo[-1].get_file()
            img = bytes(await f.download_as_bytearray())
            parts = [types.Part.from_bytes(data=img, mime_type="image/jpeg")]
        elif msg.voice:
            f = await msg.voice.get_file()
            audio = bytes(await f.download_as_bytearray())
            parts = [types.Part.from_bytes(data=audio, mime_type="audio/ogg")]
        else:
            return await msg.reply_text("Kirim teks, foto nota, atau voice note ya.")

        rows = extract(parts)
        write_rows(SHEET_ID, rows, user_label)

        ringkas = "\n".join(
            f"✅ {r['tipe']}: {r['deskripsi']} - Rp{int(r['nominal']):,}".replace(",", ".")
            for r in rows
        )
        await msg.reply_text(f"Tercatat:\n{ringkas}")

    except Exception as e:
        await msg.reply_text("Maaf, gagal memproses. Coba kirim ulang dengan lebih jelas.")
        print("ERROR:", e)

app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()

# CommandHandler didaftarkan SEBELUM MessageHandler, supaya /opencsv
# tidak ikut tertangkap filters.TEXT dan dikirim ke Gemini.
app.add_handler(CommandHandler("opencsv", opencsv))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VOICE, handle))
app.run_polling()
