import utils
import cv2
from typing import List
from char import CHAR_BITMAPS
from process_image_to_packets import process_image_to_packets
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os


def _wrap_text_force_break(text, font, max_width):
    draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    lines = []
    
    current_line = ""
    for char in text:
        try:
            # Pillow >= 10.0.0
            bbox = draw.textbbox((0, 0), current_line + char, font=font)
            next_line_width = bbox[2] - bbox[0]
        except AttributeError:
            # Older Pillow
            next_line_width, _ = draw.textsize(current_line + char, font=font)
        
        if next_line_width > max_width:
            lines.append(current_line)
            current_line = char
        else:
            current_line += char
            
    if current_line:
        lines.append(current_line)
        
    return lines


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
            line.append(i & 0xFF)
            line.append((i >> 8) & 0xFF)
            line.append(1)

            for v in self.data_array[i]:
                line.extend(bytes(v))

            line.extend(b'UU')
            buffer.append(bytes(line))

        # Printer command suffix/footer
        footer = [
            b'\xaa\xaa\x01\x01UU',
            b'\xaa\xaa\x01\x01UU',
        ]
        buffer.extend(footer)

        return buffer

    @staticmethod
    def from_string(text: str, debug_output = False):
        """
        Generates an image containing the given string and processes it.
        """
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        font_size = 24
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Wrap text to fit printer width (384px)
        text = text.replace('\n', ' ')
        wrapped_text = _wrap_text_force_break(text, font, 384)
        
        # Calculate image dimensions
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        max_line_width = 0
        total_height = 0
        line_spacing = 5

        for line in wrapped_text:
            try:
                # Pillow >= 10.0.0
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
            except AttributeError:
                # Older Pillow
                line_width, line_height = draw.textsize(line, font=font)
            
            if line_width > max_line_width:
                max_line_width = line_width
            total_height += line_height + line_spacing
            
        img_width = max_line_width + 20 # Add padding
        img_height = total_height + 10 # Add padding

        img = Image.new('L', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)

        y_text = 5 #
        for line in wrapped_text:
            try:
                # Pillow >= 10.0.0
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
            except AttributeError:
                # Older Pillow
                _, line_height = draw.textsize(line, font=font)

            draw.text((10, y_text), line, font=font, fill='black')
            y_text += line_height + line_spacing


        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_file.name)
        if debug_output:
            img.save("debug_output.png")

        # from_image expects a path, so we close the file and pass the name
        temp_file.close()

        try:
            printer_data = PrinterData.from_image(temp_file.name)
        finally:
            os.unlink(temp_file.name)

        return printer_data

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
