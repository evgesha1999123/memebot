from PIL import Image, ImageDraw, ImageFont

def save_ascii_to_jpeg(ascii_text):
    ascii_text = 'hello world!'
    fontsize = 1
    img_fraction = 0.5
    image = Image.new('RGB', (100, 100), color = (255, 255, 255))
    font = ImageFont.truetype('fonts/consola.ttf', fontsize)
    while font.getbbox(ascii_text)[0] < img_fraction*image.size[0]:
        fontsize += 1
    
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), ascii_text, fill = (0, 0, 0))
    image.save('ascii_jpeg_files/file1.jpeg')

#convert to ascii - art
def convert_to_ascii(image, new_width = 100):
    grayscale_image = pixel_to_grayscale(resize_image(image))
    new_image_data = pixel_to_ascii(grayscale_image)
    pixel_nb = len(new_image_data)
    ascii_image = '\n'.join(new_image_data[i : i + new_width] for i in range(0, pixel_nb, new_width))
    return ascii_image

#сопоставление каждого пикселя с соответствующим ascii-символом
def pixel_to_ascii(image):
    ASCII_CHAR = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    pixels = image.getdata()
    characters = ''.join(ASCII_CHAR[pixel // 25] for pixel in pixels)
    return characters

#преобразование исходного изображения в оттенки серого
def pixel_to_grayscale(image):
    grayscale_img = image.convert('L')
    return grayscale_img

#пропорционально уменьшаем картинку
def resize_image(image, new_width = 100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_img = image.resize((new_width, new_height))
    return resized_img
