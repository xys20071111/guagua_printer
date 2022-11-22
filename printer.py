from serial import Serial
from queue import Queue
import threading
from printer_data import PrinterData


class Printer(threading.Thread):
    __mission_queue = Queue()
    __print_end = b'\xaa\xaa\x0d\x01\x30\x00\x80\x01\x00\x00\x00\x00\x00\x01\x34\x01\x55\x55'
    def __init__(self, port: str) -> None:
        super().__init__()
        self.__rfcomm = Serial(port)
        self.daemon = True
        self.start()

    def add_mission(self,data: PrinterData):
        self.__mission_queue.put(data.get_printer_acceptable_data())

    def run(self) -> None:
        while True:
            self.__rfcomm.write(self.__mission_queue.get())
            while True:
                data = self.__rfcomm.read_until(b'UU')
                if data == self.__print_end:
                    break
            break