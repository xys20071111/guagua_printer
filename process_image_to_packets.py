import cv2
import numpy as np
from typing import List

def process_image_to_packets(
    image: np.ndarray,
    padding_height: int = 0,
    dithering: bool = True
) -> List[bytes]:
    """
    将 OpenCV Mat 图像转换为包含抖动处理的二值化数据包。
    该函数模拟了原始 Java 代码的核心算法。

    Args:
        image (np.ndarray): 输入的 OpenCV 图像 (建议为 BGR 或灰度图)。
        padding_height (int): 在图像底部添加的虚拟空白区域高度。
        dithering (bool): 是否启用 Floyd-Steinberg 抖动算法。

    Returns:
        List[bytes]: 一个列表，每个元素都是一个数据包（bytes 对象）。
    """
    # 1. 准备工作：转换为灰度图并创建浮点型副本用于抖动处理
    if len(image.shape) == 3 and image.shape[2] == 3: # BGR to Gray
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image.copy()

    # 使用浮点型来精确计算和扩散误差
    dither_image = gray_image.astype(np.float32)
    h, w = dither_image.shape
    total_height = h + padding_height

    packets = []

    # 2. 核心处理循环：遍历每个像素
    for y in range(total_height):
        # 如果当前行在实际图像范围内
        if y < h:
            row_bits = []
            for x in range(w):
                # A. 颜色量化
                old_pixel = dither_image[y, x]
                # 使用 128 作为阈值进行二值化
                new_pixel = 255 if old_pixel > 127 else 0

                # 收集比特：黑色(0)为'1', 白色(255)为'0'，与Java逻辑对应
                row_bits.append(1 if new_pixel == 0 else 0)

                # 更新图像像素值为量化后的值
                dither_image[y, x] = new_pixel

                # B. 误差扩散 (如果启用)
                if dithering:
                    quant_error = old_pixel - new_pixel

                    # 将误差扩散到邻近像素
                    if x + 1 < w:
                        dither_image[y, x + 1] += quant_error * 7 / 16
                    if y + 1 < h:
                        if x - 1 >= 0:
                            dither_image[y + 1, x - 1] += quant_error * 3 / 16
                        dither_image[y + 1, x] += quant_error * 5 / 16
                        if x + 1 < w:
                            dither_image[y + 1, x + 1] += quant_error * 1 / 16
        else: # 如果是填充区域，则全部视为白色
            row_bits = [0] * w

        # C. 数据打包
        # 每8个比特合并成一个字节
        row_bytes_data = []
        for i in range(0, len(row_bits), 8):
            # 取8个比特
            chunk = row_bits[i:i+8]
            # 如果不足8位，用0补齐（通常发生在宽度不是8的倍数时）
            if len(chunk) < 8:
                chunk.extend([0] * (8 - len(chunk)))

            byte_string = "".join(map(str, chunk))
            byte_value = int(byte_string, 2)
            row_bytes_data.append(byte_value)

        # 创建包头 (与Java代码结构类似)
        # byte[0] = 3 (包类型)
        # byte[1] = 行号低8位
        # byte[2] = 行号高8位
        # byte[3] = 包内有效行数 (这里简化为1，即每行一个包)
        header = [3, y & 0xFF, (y >> 8) & 0xFF, 1]

        # 组合包头和数据，并添加到结果列表
        packet = bytes(row_bytes_data)
        packets.append(packet)

    return packets


### 如何使用

# 下面是一个完整的使用示例，包括创建一个示例图像、调用函数并打印结果。

if __name__ == '__main__':
    # 1. 创建一个示例图像 (一个从黑到白的灰度渐变图)
    width, height = 96, 64
    sample_image = np.zeros((height, width), dtype=np.uint8)
    for i in range(width):
        sample_image[:, i] = int(i * (255 / width))

    dithered_packets = process_image_to_packets(
        sample_image,
        padding_height=0,
        dithering=True
    )
