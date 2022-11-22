from printer import Printer
from printer_data import PrinterData

if __name__ == '__main__':
    import time
    printer = Printer('/dev/rfcomm0')
    data = PrinterData.fromString("Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.")
    # data = PrinterData()
    # data.draw_str(time.strftime('%Y-%m-%d %H:%M:%S'))
    # data.newline()
    # data.draw_str('Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.Everything is OK.')
    printer.add_mission(data)
    printer.run()