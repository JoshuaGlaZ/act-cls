import requests
import os
import random
import json
from datetime import datetime, timedelta


def generate_unique_nrp(count=3):
    nrp_set = set()
    while len(nrp_set) < count:
        gen_random = random.randrange(20, 70)
        if str(gen_random) != os.getenv('CODE'):
            nrp_set.add(os.getenv('TMP') + str(gen_random))
    return list(nrp_set)


def read_requirement():
    try:
        with open('hour.txt', 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                raise ValueError("File does not have sufficient lines")

            start_time, end_time, identifier = lines[1:2][0].split('-')

            if len(start_time) != 4 or len(end_time) != 4:
                raise ValueError(
                    "Time components should be exactly 4 digits long.")

            t1 = f"{start_time[:2]}:{start_time[2:4]}:00"
            t2 = f"{end_time[:2]}:{end_time[2:4]}:00"

            start_dt = datetime.strptime(t1, "%H:%M:%S")
            end_dt = datetime.strptime(t2, "%H:%M:%S")

            if (end_dt - start_dt).total_seconds() > 2 * 3600:
                raise ValueError("The interval is greater than 2 hours.")
            return t1, t2, identifier
    except ValueError as ve:
        print(f"Error reading requirement file: {ve}")
        return None, None, None


def post_request():
    ls = generate_unique_nrp()
    dt = datetime.now() + timedelta(days=1)
    jam_mulai, jam_selesai, ruang = read_requirement()
    if not (jam_mulai and jam_selesai and ruang):
        print("Invalid time range or file data.")
        return

    hd = json.loads(os.getenv('HEADER_JSON'))
    pr = json.loads(os.getenv('PARAM'))
    body_params = {
        'idbiaya': '',
        'idpeminjaman': '',
        'txtMode': 'add',
        'total_detail': '3',
        'idruangpinjam': f'{ruang}',
        'tglpakai': dt.strftime('%Y-%m-%d'),
        'jam_mulai': jam_mulai,
        'jam_selesai': jam_selesai,
        'nohp': os.getenv('NOHP'),
        'tujuan_penggunaan': 'Belajar/Tugas Kelompok',
        'detail_0': 'on',
        'idanggota_0': ls[0],
        'detail_1': 'on',
        'idanggota_1': ls[1],
        'detail_2': 'on',
        'idanggota_2': ls[2]
    }

    session = requests.Session()
    session.cookies.set(os.getenv('NAME'), os.getenv('COOKIE'))

    response = session.post(
        os.getenv('URL'), params=pr, data=body_params, headers=hd)

    print("Response data:", response.text)
    print("Response code:", response.status_code)


def main():
    required_vars = ['CODE', 'COOKIE', 'HEADER_JSON',
                     'NAME', 'NOHP', 'PARAM', 'TMP', 'URL']
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing environment variable: {var}")

    try:
        post_request()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()
