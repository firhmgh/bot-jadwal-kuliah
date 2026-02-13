import random

def generate_algo(courses, rooms, days, times):
    schedule = []
    
    def is_conflict(day, time, room, dosen, kelas_lengkap):
        for s in schedule:
            if s['Hari'] == day and s['Waktu'] == time:
                if s['Ruangan'] == room or s['Dosen Pengampu'] == dosen or s['Kelas'] == kelas_lengkap:
                    return True
        return False

    for c in courses:
        assigned = False
        attempts = 0
        dosen = c['Dosen Pengampu']
        matkul = c['Mata Kuliah']
        kelas_lengkap = f"Sem{c['Semester']}-{c['Kelas']}"
        
        while not assigned and attempts < 2000:
            day = random.choice(days)
            room = random.choice(rooms)
            time_obj = random.choice(times)
            time_str = time_obj['Waktu'] 
            
            if not is_conflict(day, time_str, room, dosen, kelas_lengkap):
                schedule.append({
                    'Semester': c['Semester'],
                    'Mata Kuliah': matkul,
                    'Dosen Pengampu': dosen,
                    'Kelas': c['Kelas'],
                    'SKS': c['SKS'],
                    'Hari': day,
                    'Waktu': time_str,
                    'Ruangan': room
                })
                assigned = True
            attempts += 1
            
    return schedule