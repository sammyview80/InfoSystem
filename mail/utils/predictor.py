import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

def load_image(image_path, image_size):
    """This will load the image and convert it to numpy array"""
    # Preprocess the image
    image = resize(image_path, image_size)
    image = np.array(image)
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def predict_notice(image_path, image_size, model_path='models/notice'):
    """This will predict the notice"""
    model = load_model(os.path.join(os.getcwd(), model_path))
    image = load_image(image_path, image_size)
    prediction = model.predict(image)[0]
    p = True if prediction[0] > prediction[1] else False
    print(f'Notice {image_path}' if p else 'Non Notice')
    return p


def resize(path, image_size=224):
    img = Image.open(path)
    img = img.resize((image_size, image_size))

    # Add an alpha channel and convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    # Convert to a numpy array
    img_array = np.array(img)

    # Ensure the image has 3 channels
    if img_array.ndim == 2:
        # Add a third dimension for grayscale images
        img_array = np.expand_dims(img_array, axis=-1)
    # img_array = np.repeat(img_array, 3, axis=-1)

    return img_array