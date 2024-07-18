import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
WATERMARK_PATH = os.getenv("WATERMARK_PATH")
IMAGE_FORMATS = ['jpeg', 'png', 'bmp', 'gif']
