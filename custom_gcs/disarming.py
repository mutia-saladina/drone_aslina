from pymavlink import mavutil

# Isi disarming.py
def send_disarm_command(connection):
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        196, # MAV_CMD_COMPONENT_ARM_DISARM
        0,
        0, # 0 berarti DISARM
        0, 0, 0, 0, 0, 0
    )