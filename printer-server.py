import io
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from printer import Printer
from printer_data import PrinterData
from process_image_to_packets import process_image_to_packets

# --- 配置 ---
# !!! 重要 !!!
# 在运行前，请将此处的串口地址修改为您的打印机所连接的实际地址。
# 在 Linux 上通常是 /dev/ttyUSB0 或 /dev/ttyACM0
# 在 macOS 上可能是 /dev/cu.usbserial-XXXX
# 在 Windows 上是 COMx (例如 "COM3")
SERIAL_PORT = "/dev/rfcomm0"

# --- FastAPI 应用实例 ---
app = FastAPI(
    title="Guagua Printer Driver Server",
    description="A server to receive images and print them on a Guagua thermal printer.",
    version="1.0.0",
)

# --- 辅助函数 ---
def create_printer_data_from_image(image: np.ndarray, dithering: bool = True) -> PrinterData:
    """
    从一个Numpy图像数组创建PrinterData对象，包含了旋转、缩放和数据包转换的逻辑。
    """
    if image is None:
        raise ValueError("Invalid image data provided.")

    height, width = image.shape

    # 如果图像是横向的（宽大于高），则旋转90度
    if width > height:
        print("Image is wider than tall, rotating 90 degrees.")
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        height, width = image.shape

    # 打印机的打印宽度是384像素（48字节）。如果图像宽度不是384，则进行缩放。
    if width != 384:
        print(f"Image width is {width}, resizing to 384.")
        aspect_ratio = height / width
        new_height = int(384 * aspect_ratio)
        image = cv2.resize(image, (384, new_height))

    # 将处理后的图像转换为打印数据包
    packets = process_image_to_packets(image, dithering=dithering)

    # 创建一个PrinterData实例，其高度与数据包数量相匹配
    printer_data = PrinterData(height=len(packets))

    # 构建打印机可接受的data_array格式
    new_data_array = []
    for packet in packets:
        # 每个数据包是长度为48的bytes对象。
        # data_array需要的是一个由单字节列表组成的列表。
        row = [[byte] for byte in packet]
        new_data_array.append(row)

    printer_data.data_array = new_data_array
    return printer_data

# --- API 端点 ---
@app.post("/print-image/", summary="Upload and Print Image")
async def print_image(file: UploadFile = File(...)):
    """
    接收用户上传的图片文件，将其转换为打印数据，并通过串口发送给打印机。

    - **支持的图片格式**: `image/jpeg`, `image/png`, `image/bmp`
    - **图片处理**:
        - 自动转换为灰度图。
        - 如果图片宽度大于高度，会自动旋转90度。
        - 图片宽度会被自动缩放到384像素以适应打印机。
        - 默认启用Floyd-Steinberg抖动算法以提升打印质量。
    """
    # 检查上传的文件类型
    if file.content_type not in ["image/jpeg", "image/png", "image/bmp"]:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a JPG, PNG, or BMP image."
        )

    try:
        # 读取上传文件的二进制内容
        image_bytes = await file.read()

        # 将二进制数据转换为Numpy数组，然后解码为OpenCV图像
        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise HTTPException(status_code=400, detail="Could not decode the image. The file may be corrupt or in an unsupported format.")

        # 从图像创建PrinterData对象
        print("Processing image for printing...")
        printer_data = create_printer_data_from_image(image, dithering=True)

        # 初始化打印机并发送数据
        print(f"Sending image to printer on port: {SERIAL_PORT}")
        printer = Printer(SERIAL_PORT)
        printer.run(printer_data)
        print("Image sent successfully!")

        return {"status": "success", "message": "Image sent to printer."}

    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        # 捕获其他所有异常
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

# --- 运行服务器的说明 ---
# 要启动服务器，请在终端中运行以下命令：
#
# 1. 安装必要的 Python 包 (如果尚未安装):
#    pip install "fastapi[all]" opencv-contrib-python pyserial
#
# 2. 启动 Uvicorn 服务器:
#    uvicorn main:app --reload
#
# 启动后，您可以通过 http://127.0.0.1:8000/docs 查看 API 文档。
