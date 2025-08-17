from serial import Serial
from queue import Queue
from printer_data import PrinterData

# This byte sequence is sent by the printer to indicate the end of a print job.
PRINT_END_RESPONSE = b'\xaa\xaa\x0d\x01\x30\x00\x80\x01\x00\x00\x00\x00\x00\x01\x34\x01\x55\x55'


class Printer:
    """
    Manages the connection to the printer and processes a queue of print missions.
    """

    def __init__(self, port: str) -> None:
        self._rfcomm = Serial(port)
        self._mission_queue = Queue()

    def add_mission(self, data: PrinterData):
        """Adds a new print job to the queue."""
        # The data is converted to the printer's format when being added to the queue.
        self._mission_queue.put(data.get_printer_acceptable_data())

    def run(self) -> None:
        """
        Starts processing the print queue.
        This method will run until the queue is empty.
        """
        while not self._mission_queue.empty():
            mission_data = self._mission_queue.get()
            for buf in mission_data:
                self._rfcomm.write(buf)

            # Wait for the printer to send the 'end of print' response
            # before sending the next job.
            while True:
                response = self._rfcomm.read_until(b'UU')
                if response == PRINT_END_RESPONSE:
                    break
