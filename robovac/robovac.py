import socket
from robovac import LocalServerInfo_pb2
import random
from Crypto.Cipher import AES
from typing import Union
import struct
from enum import Enum

_AES_KEY = bytearray([0x24, 0x4E, 0x6D, 0x8A, 0x56, 0xAC, 0x87, 0x91, 0x24, 0x43, 0x2D, 0x8B, 0x6C, 0xBC, 0xA2, 0xC4])
_AES_IV = bytearray([0x77, 0x24, 0x56, 0xF2, 0xA7, 0x66, 0x4C, 0xF3, 0x39, 0x2C, 0x35, 0x97, 0xE9, 0x3E, 0x57, 0x47])


def _encrypt(data):
    cipher = AES.new(bytes(_AES_KEY), AES.MODE_CBC, bytes(_AES_IV))

    # Pad to 16 bits for AES CBC
    for i in range(16 - (len(data) % 16)):
        data += b'\0'

    return cipher.encrypt(data)


def _decrypt(data):
    cipher = AES.new(bytes(_AES_KEY), AES.MODE_CBC, bytes(_AES_IV))
    return cipher.decrypt(data)


def build_robovac_command(mode, command):
    mcu_ota_header_0xa5 = 0xA5
    cmd_data = (mode.value + command.value)

    return bytes([mcu_ota_header_0xa5, mode.value, command.value, cmd_data, 0xFA])


class RobovacModes(Enum):
    WORK = 0xE1
    SET_SPEED = 0xE8
    FIND_ME = 0xEC
    GO_FORWARD = 0xE2
    GO_LEFT = 0xE4
    GO_RIGHT = 0xE5
    GO_BACKWARD = 0xE3


class RobovacCommands(Enum):
    AUTO_CLEAN = 0x02
    SINGLE_ROOM_CLEAN = 0x05
    SPOT_CLEAN = 0x01
    EDGE_CLEAN = 0x04
    STOP_CLEAN = 0x00
    GO_HOME = 0x03

    SLOW_SPEED = 0x00
    FAST_SPEED = 0x01

    START_RING = 0x01
    STOP_RING = 0x00

    MOVE = 0x01


class RobovacStatus:
    def __init__(self,
                 find_me,
                 water_tank_status,
                 mode,
                 speed,
                 charger_status,
                 battery_capacity,
                 error_code,
                 stop):
        self.find_me = find_me
        self.water_tank_status = water_tank_status
        self.mode = mode
        self.speed = speed
        self.charger_status = charger_status
        self.battery_capacity = battery_capacity
        self.error_code = error_code
        self.stop = stop

    def __str__(self) -> str:
        return f'[FIND_ME: {self.find_me}, WATER_TANK: {self.water_tank_status}, MODE: {self.mode}, SPEED: {self.speed}, CHARGER_STATUS: {self.charger_status}, BATTERY_CAPACITY: {self.battery_capacity}, ERROR_CODE: {self.error_code}, STOP: {self.stop}]'


class Robovac:
    @staticmethod
    def _parse_local_server_message_from_decrypted_response(decrypted_response):
        # First 2 bytes indicate length of the actual data
        length = struct.unpack("<H", decrypted_response[0:2])[0]
        protobuf_data = decrypted_response[2:length + 2]

        message = LocalServerInfo_pb2.LocalServerMessage()
        message.ParseFromString(protobuf_data)
        return message

    def __init__(self, ip: str, local_code: str, port=55556):
        self.ip = ip
        self.port = port
        self.local_code = local_code
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        self.s.connect((self.ip, self.port))

    def get_status(self) -> RobovacStatus:
        message = self._build_get_device_status_user_data_message()
        robovac_response = self._send_packet(message, True)
        received_status_bytes = robovac_response.c.usr_data
        received_status_ints = [x for x in received_status_bytes]

        return RobovacStatus(
            1 if received_status_ints[6] & 4 > 0 else 0,
            1 if received_status_ints[6] & 2 > 0 else 0,
            received_status_ints[1] & 255,
            received_status_ints[8] & 255,
            received_status_ints[11] & 255,
            received_status_ints[10] & 255,
            received_status_ints[12] & 255,
            received_status_ints[13] & 255
        )

    def start_auto_clean(self):
        command = build_robovac_command(RobovacModes.WORK, RobovacCommands.AUTO_CLEAN)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def start_spot_clean(self):
        command = build_robovac_command(RobovacModes.WORK, RobovacCommands.SPOT_CLEAN)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def start_edge_clean(self):
        command = build_robovac_command(RobovacModes.WORK, RobovacCommands.EDGE_CLEAN)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def start_single_room_clean(self):
        command = build_robovac_command(RobovacModes.WORK, RobovacCommands.SINGLE_ROOM_CLEAN)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def stop(self):
        command = build_robovac_command(RobovacModes.WORK, RobovacCommands.STOP_CLEAN)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def go_home(self):
        command = build_robovac_command(RobovacModes.WORK, RobovacCommands.GO_HOME)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def start_find_me(self):
        command = build_robovac_command(RobovacModes.FIND_ME, RobovacCommands.START_RING)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def stop_find_me(self):
        command = build_robovac_command(RobovacModes.FIND_ME, RobovacCommands.STOP_RING)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def use_normal_speed(self):
        command = build_robovac_command(RobovacModes.SET_SPEED, RobovacCommands.SLOW_SPEED)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def use_max_speed(self):
        command = build_robovac_command(RobovacModes.SET_SPEED, RobovacCommands.FAST_SPEED)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def go_forward(self):
        command = build_robovac_command(RobovacModes.GO_FORWARD, RobovacCommands.MOVE)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def go_backward(self):
        command = build_robovac_command(RobovacModes.GO_BACKWARD, RobovacCommands.MOVE)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def go_left(self):
        command = build_robovac_command(RobovacModes.GO_LEFT, RobovacCommands.MOVE)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def go_right(self):
        command = build_robovac_command(RobovacModes.GO_RIGHT, RobovacCommands.MOVE)
        message = self._build_command_user_data_message(command)

        self._send_packet(message, False)

    def _build_command_user_data_message(self, command_payload) -> LocalServerInfo_pb2.LocalServerMessage:
        magic_number = self._get_magic_number()
        message = LocalServerInfo_pb2.LocalServerMessage()
        message.magic_num = magic_number
        message.localcode = self.local_code
        message.c.type = 0
        message.c.usr_data = command_payload

        return message

    def _build_get_device_status_user_data_message(self) -> LocalServerInfo_pb2.LocalServerMessage:
        magic_number = self._get_magic_number()
        message = LocalServerInfo_pb2.LocalServerMessage()
        message.localcode = self.local_code
        message.magic_num = magic_number
        message.c.type = 1

        return message

    def _get_magic_number(self) -> int:
        ping = LocalServerInfo_pb2.LocalServerMessage()
        ping.localcode = self.local_code
        ping.magic_num = random.randrange(3000000)

        ping.a.type = 0

        pong = self._send_packet(ping, True)
        return pong.magic_num + 1

    def _send_packet(self,
                     packet: LocalServerInfo_pb2.LocalServerMessage,
                     receive: True) -> Union[None, LocalServerInfo_pb2.LocalServerMessage]:
        raw_packet_data = packet.SerializeToString()
        encrypted_packet_data = _encrypt(raw_packet_data)

        try:
            self.s.send(encrypted_packet_data)
        except:
            self.connect()
            self.s.send(encrypted_packet_data)

        if not receive:
            return None

        response_from_robovac = self.s.recv(1024)
        decrypted_response = _decrypt(response_from_robovac)
        return Robovac._parse_local_server_message_from_decrypted_response(decrypted_response)
