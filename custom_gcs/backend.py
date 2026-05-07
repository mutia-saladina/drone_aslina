# from pymavlink import mavutil

# # 1. Establish connection
# # Replace 'COM3' or '/dev/ttyUSB0' with your specific radio port
# connection = mavutil.mavlink_connection('COM3', baud=57600)

# # 2. Wait for a heartbeat to confirm the link is active
# print("Waiting for heartbeat...")
# connection.wait_heartbeat()
# print(f"Heartbeat from system {connection.target_system} component {connection.target_component}")

# # 3. Read specific telemetry data in a loop
# while True:
#     try:
#         # Fetch 'ATTITUDE' data
#         msg = connection.recv_match(type='ATTITUDE', blocking=True)
#         if msg:
#             print(f"Roll: {msg.roll}, Pitch: {msg.pitch}, Yaw: {msg.yaw}"
#     except KeyboardInterrupt:
#         break

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from pymavlink import mavutil
import threading
import time

# 1. Setup Flask & SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 2. Koneksi MAVLink (Ganti ke /dev/ttyUSB0 untuk Ubuntu kamu)
connection = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)


def fetch_telemetry():
    print("Waiting for heartbeat...")
    connection.wait_heartbeat()
    print(f"Heartbeat dari system {connection.target_system}")

    while True:
        try:
            # Ambil data ATTITUDE (Roll, Pitch, Yaw)
            msg = connection.recv_match(type='ATTITUDE', blocking=True)

            # Ambil juga data POSITION jika kamu butuh Lat/Lng sesuai HTML kamu
            msg_pos = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=False)

            if msg:
                # Bungkus data ke dalam dictionary 'telemetry'
                telemetry = {
                    'roll': msg.roll,
                    'pitch': msg.pitch,
                    'yaw': msg.yaw,
                    'lat': 0,  # Default jika GPS belum fix
                    'lng': 0,
                    'alt': 0
                }

                # Jika data posisi tersedia, masukkan ke dictionary
                if msg_pos:
                    telemetry['lat'] = msg_pos.lat / 1.0e7
                    telemetry['lng'] = msg_pos.lon / 1.0e7
                    telemetry['alt'] = msg_pos.relative_alt / 1000.0

                # Kirim ke HTML
                socketio.emit('telemetry_data', telemetry)

                # Print di terminal untuk debugging
                print(f"Sent -> Roll: {msg.roll:.2f}, Pitch: {msg.pitch:.2f}, Yaw: {msg.yaw:.2f}")

        except Exception as e:
            print(f"Error: {e}")
            break
        time.sleep(0.1)


# Jalankan MAVLink di background thread
thread = threading.Thread(target=fetch_telemetry)
thread.daemon = True
thread.start()

if __name__ == '__main__':
    # Jalankan server di port 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
