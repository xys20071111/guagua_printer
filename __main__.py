from printer import Printer
from printer_data import PrinterData

if __name__ == '__main__':
    data_1 = PrinterData(128)
    data_1.draw_str('#include<stdio.h>')
    data_1.newline()
    data_1.draw_str('int main(){')
    data_1.newline()
    data_1.draw_str('    printf("abc123ABC!");')
    data_1.newline()
    data_1.draw_str('    return 0;')
    data_1.newline()
    data_1.draw_str('}')
    printer = Printer('/dev/rfcomm0')
    printer.add_mission(data_1)
    printer.print()
    