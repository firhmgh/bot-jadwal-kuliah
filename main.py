import telebot
import os
from dotenv import load_dotenv
from database import get_connection
from scheduler import generate_algo
from keep_alive import keep_alive

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = (
        "👋 Selamat datang di Bot Jadwal Kuliah (Versi Python) \n\n"
        "📅 !generate  → Generate jadwal otomatis\n"
        "➕ !tambah    → Tambah data manual\n"
        "🔍 !cek [keyword] → Cari jadwal"
    )
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == '!generate')
def handle_generate(message):
    bot.reply_to(message, "⏳ Sedang menyusun jadwal, mohon tunggu...")
    
    try:
        sh = get_connection()
        
        courses = sh.worksheet("matakuliah").get_all_records()
        rooms_data = sh.worksheet("ruangan").get_all_records()
        rooms = [r['Ruangan'] for r in rooms_data] 
        days_data = sh.worksheet("hari").get_all_records()
        days = [d['Hari'] for d in days_data]
        times = sh.worksheet("jadwal").get_all_records()
        
        final_schedule = generate_algo(courses, rooms, days, times)
        
        ws_final = sh.worksheet("JadwalFinal")
        ws_final.clear() # Hapus lama
        
        headers = ['Semester', 'Mata Kuliah', 'Dosen Pengampu', 'Kelas', 'SKS', 'Hari', 'Waktu', 'Ruangan']
        data_to_write = [headers]
        
        for item in final_schedule:
            row = [item[h] for h in headers]
            data_to_write.append(row)
            
        ws_final.update('A1', data_to_write)
        bot.reply_to(message, f"✅ Sukses! {len(final_schedule)} jadwal berhasil digenerate.")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(func=lambda m: m.text.lower().startswith('!cek'))
def handle_cek(message):
    query = message.text.replace("!cek", "").strip().lower()
    if not query:
        bot.reply_to(message, "⚠️ Ketik kata kunci. Contoh: `!cek senin`")
        return

    try:
        sh = get_connection()
        ws_final = sh.worksheet("JadwalFinal")
        all_data = ws_final.get_all_records()
        
        results = []
        for row in all_data:
            row_str = " ".join([str(v) for v in row.values()]).lower()
            if query in row_str:
                results.append(row)
        
        if not results:
            bot.reply_to(message, "❌ Data tidak ditemukan.")
        else:
            response = f"🔍 Ditemukan {len(results)} data:\n\n"
            for r in results[:10]:
                response += f"🕒 {r['Hari']}, {r['Waktu']} ({r['Ruangan']})\n📚 {r['Mata Kuliah']}\n👨‍🏫 {r['Dosen Pengampu']}\n---\n"
            bot.reply_to(message, response)
            
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

print("Bot sedang berjalan...")

keep_alive()

bot.infinity_polling()