from serial import Serial
from printer_data import PrinterData

# This byte sequence is sent by the printer to indicate the end of a print job.
PRINT_END_RESPONSE = b'\xaa\xaa\x0d\x01\x30\x00\x80\x01\x00\x00\x00\x00\x00\x01\x34\x01\x55\x55'


class Printer:
    """
    Manages the connection to the printer and processes a queue of print missions.
    """

    def __init__(self, port: str) -> None:
        self._rfcomm = Serial(port)

    def run(self, mission: PrinterData) -> None:
        """
        Starts processing the print queue.
        This method will run until the queue is empty.
        """
        mission_data = mission.get_printer_acceptable_data()
        for buf in mission_data:
            self._rfcomm.write(buf)
