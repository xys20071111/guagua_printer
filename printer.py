from serial import Serial
from printer_data import PrinterData


class Printer:
    __mission_queue = []
    __first_print = True
    __print_end = b'\xaa\xaa\x0d\x01\x30\x00\x80\x01\x00\x00\x00\x00\x00\x01\x34\x01\x55\x55'
    def __init__(self, port: str) -> None:
        super().__init__()
        self.__rfcomm = Serial(port)

    def add_mission(self,data: PrinterData):
        self.__mission_queue.insert(0,data.get_printer_acceptable_data())

    def print(self) -> None:
        for i in range(0,len(self.__mission_queue)):
            self.__rfcomm.write(self.__mission_queue[i])
            while True:
                data = self.__rfcomm.read_until(b'UU')
                if data == self.__print_end:
                    break