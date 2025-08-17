import utils
import cv2
from typing import List
from char import CHAR_BITMAPS
from process_image_to_packets import process_image_to_packets


class PrinterData:
    """
    Represents the printer's canvas and provides methods to draw text and
    generate the final data payload for printing.
    """

    def __init__(self, height=255) -> None:
        self._height = height
        self._cursor_x = 4  # Start drawing from line 4
        self._cursor_y = 0
        self.data_array = self._create_empty_canvas()

    def _create_empty_canvas(self):
        """Creates a blank data array (canvas) of the specified height."""
        return [[[0] for _ in range(48)] for _ in range(self._height)]

    def newline(self):
        """Moves the cursor to the next line."""
        self._cursor_x += 23
        self._cursor_y = 0

    def clean_canvas(self):
        """Clears the canvas."""
        self.data_array = self._create_empty_canvas()

    def draw(self, ch: str, x: int, y: int):
        """Draws a single character at a specific coordinate."""
        if len(ch) > 1:
            raise utils.TooManyCharException
        if x < 4:
            raise utils.ReserveLineException

        char_data = CHAR_BITMAPS[ch]
        char_shape = utils.get_shape(char_data)

        for i in range(char_shape[1]):
            for j in range(char_shape[0]):
                self.data_array[x + i][y + j] = char_data[i][j]

    def draw_str(self, text: str):
        """Draws a string of text, handling line wraps."""
        for char_to_draw in text:
            if char_to_draw == '\n':
                self.newline()
                continue
            char_data = CHAR_BITMAPS[char_to_draw]
            char_shape = utils.get_shape(char_data)

            if char_shape[0] + self._cursor_y > 48:
                self.newline()
                if self._cursor_x >= self._height:
                    raise utils.TooLongException

            self.draw(char_to_draw, self._cursor_x, self._cursor_y)
            self._cursor_y += char_shape[0]


    def get_printer_acceptable_data(self) -> List[bytes]:
        """
        Assembles the complete data payload with headers, canvas data, and footers
        in a format the printer can understand.
        """
        count = 0

        # Printer command prefix/header
        header = [
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x01\xacUU',
            b'\xaa\xaa\x01\xacUU',
            b'\xaa\xaa\x01\x04UU',
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x08\x02\xb6\x00\x00\x00\x00\x01\x1bUU',
        ]

        buffer = [bytes(item) for item in header]

        for i in range(self._height):
            line = bytearray()
            line.extend(b'\xaa\xaa\x34\x03')

            # Handle data chunking for heights > 255
            # if i == 256: # Note: original code had `and (i != 0)` which is redundant
            #     count += 1

            line.append(i & 0xFF)
            line.append((i >> 8) & 0xFF)
            line.append(1)

            for v in self.data_array[i]:
                line.extend(bytes(v))

            line.extend(b'UU')
            print(len(line)-5)
            buffer.append(bytes(line))

        # Printer command suffix/footer
        footer = [
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x01\x01UU',
        ]
        buffer.extend(footer)

        return buffer

    @staticmethod
    def from_string(text: str):
        """
        Calculates the required canvas height for a given string and returns
        a PrinterData instance with the string already drawn on it.
        """
        cursor_x = 4
        cursor_y = 0

        # Calculate required height
        for char_to_measure in text:
            if char_to_measure == '\n':
                cursor_x += 23
                cursor_y = 0
                continue
            char_data = CHAR_BITMAPS[char_to_measure]
            char_shape = utils.get_shape(char_data)
            if char_shape[0] + cursor_y > 48:
                cursor_x += 23
                cursor_y = 0
            cursor_y += char_shape[0]

        # Add final padding
        final_height = cursor_x + 23

        result = PrinterData(final_height)
        result.draw_str(text)
        return result

    @staticmethod
    def from_image(image_path: str, dithering: bool = True):
        """
        Creates a PrinterData object from an image file.
        If the image is wider than it is tall, it will be rotated.
        """
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        height, width = image.shape

        # If the image is wider than it is tall, rotate it.
        if width > height:
            print("Image is wider than tall, rotating 90 degrees.")
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            height, width = image.shape

        # The printer's width is 384 pixels, which is 48 bytes.
        # If the image width is not 384, it should be resized.
        if width != 384:
            print(f"Image width is {width}, resizing to 384.")
            aspect_ratio = height / width
            new_height = int(384 * aspect_ratio)
            image = cv2.resize(image, (384, new_height))

        packets = process_image_to_packets(image, dithering=dithering)

        # The height of the printer data should match the number of packets.
        printer_data = PrinterData(height=len(packets))

        new_data_array = []
        for packet in packets:
            # Each packet is a bytes object of length 48.
            # The data_array needs to be a list of lists of single-byte lists.
            row = [[byte] for byte in packet]
            new_data_array.append(row)

        printer_data.data_array = new_data_array

        return printer_data
