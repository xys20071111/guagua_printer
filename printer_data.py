import utils
import char as char_dict

class PrinterData:
    __x = 4
    __y = 0
    def __init__(self, height=255) -> None:
        self.__height = height
        data_array = []
        for i in range(0, height):
            data = []
            for j in range(0, 48):
                data.append(bytes([0]))
            data_array.append(data)
        self.data_array = data_array
    def newline(self):
        self.__x += 23
        self.__y = 0
    def clean_canvas(self):
        data_array = []
        for i in range(0, self.__height):
            data = []
            for j in range(0, 48):
                data.append(bytes([0]))
            data_array.append(data)
        self.data_array = data_array

    def draw(self, ch:str, x:int, y:int):
        if len(ch) > 1:
            raise utils.TooManyCharException
        char = char_dict.char[ch]
        char_shape = utils.get_shape(char)
        if x < 4:
            raise utils.ReserveLineException
        char = char_dict.char[ch]
        for i in range(0, char_shape[1]):
            for j in range(0, char_shape[0]):
                self.data_array[x+i][y+j] = char[i][j]

    def draw_str(self,text:str):
        for i in range(0, len(text)):
            char = char_dict.char[text[i]]
            char_shape = utils.get_shape(char)
            if(char_shape[0] + self.__y > 48):
                self.__x += 23
                self.__y = 0
                if self.__x > self.__height:
                    raise utils.TooLongException
            self.draw(text[i],self.__x,self.__y)
            self.__y += char_shape[0]

    def get_printer_acceptable_data(self):
        count = 0
        buffer = [
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x01\xacUU',
            b'\xaa\xaa\x01\xacUU',
            b'\xaa\xaa\x01\x04UU',
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x08\x02\xb6\x00\x00\x00\x00\x01\x1bUU',
        ]
        for i in range(0, self.__height):
            line = bytes()
            line += b'\xaa\xaa4\x03'
            if(i == 256) and (i != 0):
                count += 1
            line += bytes([i % 256])
            line += bytes([count])
            line += b'\x01'
            for v in self.data_array[i]:
                if type(v) == int:
                    line += bytes([v])
                else:
                    line += v
            line += b'UU'
            buffer.append(line)
        buffer.append(b'\xaa\xaa\x01\x01UU')
        buffer.append(b'\xaa\xaa\x01\x01UU')
        return bytes().join(buffer)

