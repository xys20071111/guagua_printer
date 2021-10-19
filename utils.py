def get_shape(d: tuple):
    height = len(d)
    width = len(d[0])
    return (width, height)

class TooHighException(Exception):
    def __str__(self) -> str:
        return "Height cannot bigger than 255."

class TooLongException(Exception):
    def __str__(self) -> str:
        return "Text longer than max height or width."

class ReserveLineException(Exception):
    def __str__(self) -> str:
        return "Line 1 to Line 3 is reserved."

class TooManyCharException(Exception):
    def __str__(self) -> str:
        return "draw function can only accept a character onec a time."