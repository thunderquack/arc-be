import io
from PIL import Image


def resize_image(image_data, width):
    image = Image.open(io.BytesIO(image_data))
    ratio = width / float(image.size[0])
    height = int((float(image.size[1]) * float(ratio)))
    resized_image = image.resize((width, height), Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    resized_image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()