from printer import Printer
from printer_data import PrinterData

if __name__ == '__main__':
    # --- Example Usage ---

    # Set the printer's device port.
    # On Linux, this might be /dev/rfcomm0, /dev/ttyUSB0, etc.
    # On Windows, this would be something like 'COM3'.
    PRINTER_PORT = '/dev/rfcomm0'

    # Create a printer instance.
    printer = Printer(PRINTER_PORT)

    # --- Create and add print missions ---

    # Mission 1: A long string that will likely wrap.
    long_text = "Everything is OK." * 10
    mission1_data = PrinterData.from_string(long_text)
    printer.add_mission(mission1_data)

    # Mission 2: A short string.
    mission2_data = PrinterData.from_string("123456")
    printer.add_mission(mission2_data)

    # Add more missions as needed...
    # import time
    # mission3_data = PrinterData.from_string(time.strftime('%Y-%m-%d %H:%M:%S'))
    # printer.add_mission(mission3_data)

    # Start the print job.
    # This will process all missions in the queue.
    print("Starting printer...")
    printer.run()
    print("All print missions completed.")
