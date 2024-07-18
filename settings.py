import os
from dotenv import load_dotenv

load_dotenv()

WATERMARK_PATH = os.getenv("WATERMARK_PATH")
IMAGE_FORMATS = ['jpeg', 'png', 'bmp', 'gif']
