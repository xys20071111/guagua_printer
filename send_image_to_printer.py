from printer import Printer
from printer_data import PrinterData
import sys

def main():
    """
    Main function to send an image to the printer.
    """
    if len(sys.argv) < 3:
        print("Usage: python send_image_to_printer.py <image_path> <serial_port>")
        print("Example: python send_image_to_printer.py my_image.png /dev/ttyUSB0")
        sys.exit(1)

    image_path = sys.argv[1]
    serial_port = sys.argv[2]

    print(f"Processing image: {image_path}")
    try:
        printer_data = PrinterData.from_image(image_path, dithering=True)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during image processing: {e}")
        sys.exit(1)

    print(f"Sending image to printer on port: {serial_port}")

    try:
        printer = Printer(serial_port)
        printer.run(printer_data)
        print("Image sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending data to the printer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
