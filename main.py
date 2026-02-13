import telebot
from telebot import types
import os
from dotenv import load_dotenv
from database import get_connection
from scheduler import generate_schedule_logic
from keep_alive import keep_alive
import time

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = (
        "👋 Selamat datang di Bot Jadwal Kuliah Otomatis\n\n"
        "Gunakan perintah berikut (WAJIB pakai tanda !):\n"
        "📅 !generate  → Generate jadwal otomatis\n"
        "➕ !tambah    → Tambah jadwal manual\n"
        "🗑️ !hapus      → Hapus jadwal\n"
        "🔍 !cek          → Cari jadwal"
    )
    bot.reply_to(message, msg)

# --- !GENERATE COMMAND 
@bot.message_handler(func=lambda m: m.text.lower().strip() == '!generate')
def handle_generate(message):
    bot.reply_to(message, "⏳ Sedang meng-generate jadwal (Algoritma Anti-Bentrok)...")
    
    try:
        sh = get_connection()
        
        ws_matkul = sh.worksheet("matakuliah")
        ws_ruang = sh.worksheet("ruangan")
        ws_hari = sh.worksheet("hari")
        ws_waktu = sh.worksheet("jadwal")
        
        courses = ws_matkul.get_all_records()
        rooms_data = ws_ruang.get_all_records()
        rooms = [r['Ruangan'] for r in rooms_data if r['Ruangan']] 
        days_data = ws_hari.get_all_records()
        days = [d['Hari'] for d in days_data if d['Hari']]
        times = ws_waktu.get_all_records()
        
        final_schedule = generate_schedule_logic(courses, rooms, days, times)
        
        ws_final = sh.worksheet("jadwalfinal")
        ws_final.clear()
        
        headers = ['Semester', 'Mata Kuliah', 'Dosen Pengampu', 'Kelas', 'SKS', 'Hari', 'Waktu', 'Ruangan']
        ws_final.append_row(headers)
        
        rows_to_add = []
        for item in final_schedule:
            rows_to_add.append([item.get(h, '') for h in headers])
            
        if rows_to_add:
            ws_final.append_rows(rows_to_add)
            
        bot.reply_to(message, f"Jadwal generated successfully! ✅\nTotal: {len(rows_to_add)} data.")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# --- !TAMBAH COMMAND 
@bot.message_handler(func=lambda m: m.text.lower().startswith('!tambah'))
def handle_tambah(message):
    text = message.text
    lines = [line.strip() for line in text.split('\n') if line.strip() != '']
    
    if len(lines) == 1:
        reply = (
            "📋 **TEMPLATE TAMBAH DATA**\n\n"
            "Silakan Copy, Paste, lalu isi di bawah setiap baris:\n\n"
            "`!tambah\n[Semester]\n[Mata Kuliah]\n[Nama Dosen]\n[Kelas]\n[SKS]\n[Hari]\n[Jam]\n[Ruangan]`\n\n"
            "⬇️ **Contoh Pengisian:**\n"
            "`!tambah\n2\nRobotika\nDr. Strange\nA\n3\nSenin\n08.00 - 10.00\nR15`"
        )
        bot.reply_to(message, reply, parse_mode="Markdown")
        return

    if len(lines) < 9:
        bot.reply_to(message, f"❌ **Data Kurang Lengkap!**\nButuh 9 baris, terdeteksi {len(lines)} baris.")
        return

    try:
        sh = get_connection()
        ws_matkul = sh.worksheet("matakuliah") 
        
        new_row = [
            lines[1], # Semester
            lines[2], # Mata Kuliah
            lines[3], # Dosen Pengampu
            lines[4], # Kelas
            lines[5], # SKS
            lines[6], # Hari
            lines[7], # Waktu
            lines[8]  # Ruangan
        ]
        
        ws_matkul.append_row(new_row)
        
        reply = (
            "✅ **Jadwal Berhasil Disimpan ke Database Matkul!**\n\n"
            f"🎓 **Semester {lines[1]}** (Kelas {lines[4]} • {lines[5]} SKS)\n"
            f"📚 {lines[2]}\n"
            f"👨‍🏫 {lines[3]}\n"
            f"🗓️ {lines[6]}\n"
            f"⏰ {lines[7]}\n"
            f"🏢 Ruangan {lines[8]}\n\n"
            "💡 _Data ini akan masuk jadwal saat !generate berikutnya_"
        )
        bot.reply_to(message, reply, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Gagal menyimpan: {str(e)}")

@bot.message_handler(func=lambda m: m.text.lower().startswith('!hapus'))
def handle_hapus(message):
    query = message.text.replace("!hapus", "").strip().lower()
    
    if not query:
        bot.reply_to(message, "⚠️ Masukkan kata kunci. Contoh: `!hapus Robotika`")
        return
        
    try:
        sh = get_connection()
        ws_final = sh.worksheet("jadwalfinal") 
        all_data = ws_final.get_all_records()
        
        found_index = -1
        data_found = {}
        
        for i, item in enumerate(all_data):
            raw_data = f"{item.get('Mata Kuliah','')} {item.get('Dosen Pengampu','')}".lower()
            if query in raw_data:
                found_index = i
                data_found = item
                break
        
        if found_index == -1:
            bot.reply_to(message, f"❌ Data \"{query}\" tidak ditemukan di Jadwal Final.")
            return
            
        row_number = found_index + 2
        ws_final.delete_rows(row_number)
        
        reply = (
            "🗑️ **Data Berhasil Dihapus!**\n\n"
            f"📚 {data_found.get('Mata Kuliah')}\n"
            f"👨‍🏫 {data_found.get('Dosen Pengampu')}\n"
            f"📍 {data_found.get('Hari')} • {data_found.get('Waktu')}\n"
        )
        bot.reply_to(message, reply, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# --- !CEK COMMAND (Logic Node 'Filter Schedule Results') ---
@bot.message_handler(func=lambda m: m.text.lower().startswith('!cek'))
def handle_cek(message):
    query = message.text.replace("!cek", "").strip().lower()
    
    if '1 siang' in query: query = '13'
    elif '2 siang' in query: query = '14'
    elif '3 sore' in query: query = '15'
    elif 'jam 8' in query: query = '08'
    
    if not query:
        bot.reply_to(message, "⚠️ Ketik kata kunci. Contoh: `!cek senin` atau `!cek robotika`")
        return

    try:
        sh = get_connection()
        ws_final = sh.worksheet("jadwalfinal")
        all_schedule = ws_final.get_all_records()
        
        filtered = []
        for item in all_schedule:
            raw_data = (
                f"Semester: {item.get('Semester')} Matkul: {item.get('Mata Kuliah')} "
                f"Dosen: {item.get('Dosen Pengampu')} Kelas: {item.get('Kelas')} "
                f"Hari: {item.get('Hari')} Waktu: {item.get('Waktu')} "
                f"Ruang: {item.get('Ruangan')}"
            ).lower()
            
            if query in raw_data:
                filtered.append(item)
        
        if not filtered:
            bot.reply_to(message, f"❌ Tidak ditemukan data untuk: \"{query}\"")
        else:
            response_text = f"🔍 **Hasil Pencarian: \"{query}\"**\n(Ditemukan: {len(filtered)} Data)\n\n"
            
            for f in filtered[:15]:
                response_text += (
                    f"🕒 **{f.get('Hari')}, {f.get('Waktu')}** ({f.get('Ruangan')})\n"
                    f"📚 {f.get('Mata Kuliah')}\n"
                    f"🎓 Sem {f.get('Semester')} • Kls {f.get('Kelas')} • {f.get('SKS')} SKS\n"
                    f"👨‍🏫 {f.get('Dosen Pengampu')}\n"
                    "-------------------\n"
                )
            
            if len(filtered) > 15:
                response_text += f"\n⚠️ ...dan {len(filtered) - 15} jadwal lainnya."
                
            bot.reply_to(message, response_text, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    
    print("Menghapus webhook lama...")
    bot.remove_webhook() 
    
    print("Bot sedang berjalan...")
    bot.infinity_polling()