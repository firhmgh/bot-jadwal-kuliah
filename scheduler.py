import random

def generate_schedule_logic(courses, rooms, days, times):
    schedule = []
    
    def is_conflict(day, time, room, dosen, kelas_lengkap):
        for s in schedule:
            if s['Hari'] == day and s['Waktu'] == time:
                if (s['Ruangan'] == room or 
                    s['Dosen Pengampu'] == dosen or 
                    s['Kelas'] == kelas_lengkap):
                    return True
        return False

    for c in courses:
        assigned = False
        attempts = 0
        
        dosen_name = c.get('Dosen Pengampu', '')
        matkul_name = c.get('Mata Kuliah', '')
        semester = c.get('Semester', '')
        kelas = c.get('Kelas', '')
        sks = c.get('SKS', '')
        kelas_lengkap = f"Sem{semester}-{kelas}"
        
        while not assigned and attempts < 2000:
            day = random.choice(days)
            room = random.choice(rooms)
            time_obj = random.choice(times)
            
            time_str = time_obj.get('Waktu') or time_obj.get('Jam') or list(time_obj.values())[0]

            if not is_conflict(day, time_str, room, dosen_name, kelas_lengkap):
                schedule.append({
                    'Semester': semester,
                    'Mata Kuliah': matkul_name,
                    'Dosen Pengampu': dosen_name,
                    'Kelas': kelas,
                    'SKS': sks,
                    'Hari': day,
                    'Waktu': time_str,
                    'Ruangan': room
                })
                assigned = True
            attempts += 1
            
    return schedule