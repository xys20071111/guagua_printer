def get_shape(d: tuple):
    height = len(d)
    width = len(d[0])
    return (width, height)

class TooHighException(Exception):
    def __str__(self) -> str:
        return "Height cannot bigger than 255"