import serial
import struct
from typing import Any
from crc import calcula_CRC


class UART_CLASS():
    SERIAL = serial.Serial("/dev/serial0", 9600)

    def get_ti(self) -> float:
        cmd = bytearray([0x01, 0x23, 0xC1])
        return self.__send_cmd(cmd, res_type='f')

    def get_tr(self) -> float:
        cmd = bytearray([0x01, 0x23, 0xC2])
        return self.__send_cmd(cmd, res_type='f')

    def get_user_input(self) -> int:
        cmd = bytearray([0x01, 0x23, 0xC3])
        return self.__send_cmd(cmd, res_type='i')

    def send_control_signal(self, value: int) -> None:
        cmd = bytearray([0x01, 0x16, 0xD1])
        return self.__send_cmd(cmd, data=value, data_type='i', size_res=0)

    def send_reference_temperature(self, value: float) -> None:
        cmd = bytearray([0x01, 0x16, 0xD2])
        return self.__send_cmd(cmd, data=value, data_type='f', size_res=0)

    def send_system_state(self, value: int) -> int:
        cmd = bytearray([0x01, 0x16, 0xD3])
        return self.__send_cmd(cmd, data=value, data_type='B', res_type='i')

    def send_control_mode(self, value: int) -> int:
        cmd = bytearray([0x01, 0x16, 0xD4])
        return self.__send_cmd(cmd, data=value, data_type='B', res_type='i')

    def send_operation_state(self, value: int) -> int:
        cmd = bytearray([0x01, 0x16, 0xD5])
        return self.__send_cmd(cmd, data=value, data_type='B', res_type='i')

    def send_room_temperature(self, value: float) -> None:
        cmd = bytearray([0x01, 0x16, 0xD6])
        return self.__send_cmd(cmd, data=value, data_type='f', size_res=0)

    def __send_cmd(self, cmd: bytearray, data: Any = 0,
                   data_type: str = '', size_res: int = 9,
                   res_type: str = '') -> Any:
        self.__insert_enrollment(cmd)
        if data_type:
            self.__insert_data(cmd, data, data_type)
        self.__insert_crc(cmd)
        self.SERIAL.write(cmd)
        res: bytearray = self.SERIAL.read(size=size_res)
        if not size_res:
            return None
        if size_res > 2 and self.__is_valid_crc(res):
            return struct.unpack(res_type, res[3:7])[0]
        else:
            return -1

    def __insert_enrollment(self, cmd: bytearray) -> None:
        cmd.extend(bytearray([0, 2, 7, 2]))

    def __insert_data(self, cmd: bytearray, data: Any, data_type: str) -> None:
        cmd.extend(struct.pack(data_type, data))

    def __insert_crc(self, cmd: bytearray) -> None:
        crc_value = calcula_CRC(cmd)
        cmd.extend([0x00FF & crc_value, 
                   (0xFF00 & crc_value) >> 8])

    def __is_valid_crc(self, res: bytearray) -> bool:
        crc_res = calcula_CRC(res[:-2])
        return ((res[-2] == (0x00FF & crc_res)) and
                (res[-1] == ((0xFF00 & crc_res) >> 8)))
