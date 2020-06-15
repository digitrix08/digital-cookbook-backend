import uuid
import os


def get_image_path(instance, image_name: str):
    image_extension = image_name.split('.')[-1]
    filename = f"{uuid.uuid4()}.{image_extension}"
    return os.path.join('uploads/recipes/', filename)
