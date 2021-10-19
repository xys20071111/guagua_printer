import utils

class PrinterData:
    def __init__(self, height=255) -> None:
        if height > 255:
            raise utils.TooHighException
        self.height = height
        data_array = []
        for i in range(0, height):
            data = []
            for j in range(0, 48):
                data.append(bytes([0]))
            data_array.append(data)
        self.data_array = data_array

    def clean_canvas(self):
        data_array = []
        for i in range(0, self.height):
            data = []
            for j in range(0, 48):
                data.append(bytes([0]))
            data_array.append(data)
        self.data_array = data_array

    def get_printer_acceptable_data(self):
        buffer = [
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x01\xacUU',
            b'\xaa\xaa\x01\xacUU',
            b'\xaa\xaa\x01\x04UU',
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x08\x02\xb6\x00\x00\x00\x00\x01\x1bUU',
        ]
        for i in range(0, self.height):
            line = bytes()
            line += b'\xaa\xaa4\x03'
            line += bytes([i % 256])
            line += b'\x00\x01'
            for v in self.data_array[i]:
                line += v
            line += b'UU'
            buffer.append(line)
        buffer.append(b'\xaa\xaa\x01\x01UU')
        buffer.append(b'\xaa\xaa\x01\x01UU')
        return bytes().join(buffer)

if __name__ == '__main__':
    import serial
    rfcomm = serial.Serial('/dev/rfcomm0',baudrate=115200)
    data = PrinterData().get_printer_acceptable_data()
    print('data ok')
    print(data)
    rfcomm.write(data)