from printer import Printer
from printer_data import PrinterData

# A simple ASCII art representation of the Gemini Logo, suitable for a narrow printer.
GEMINI_LOGO_ASCII = r"""

     *
    ***
   *****
  *******
     ***
     ***

"""

if __name__ == "__main__":
    # --- Printer Setup ---
    # Set the printer's device port.
    # On Linux, this might be /dev/rfcomm0, /dev/ttyUSB0, etc.
    # On Windows, this would be something like 'COM3'.
    PRINTER_PORT = '/dev/rfcomm0'

    # Create a printer instance.
    printer = Printer(PRINTER_PORT)

    # --- Create and add the print mission ---
    print("Creating print mission for Gemini logo...")
    gemini_mission_data = PrinterData.from_string(GEMINI_LOGO_ASCII)
    printer.add_mission(gemini_mission_data)
    with open('test.bin', mode='wb') as f:
        f.write(gemini_mission_data.get_printer_acceptable_data())
    # # --- Run the printer ---
    # print(f"Sending art to printer on {PRINTER_PORT}...")
    # printer.run()
    # print("Print mission for Gemini logo completed.")
