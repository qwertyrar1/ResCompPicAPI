from logging import getLogger

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from settings import WATERMARK_PATH
from PIL import Image
import io

from api.image_processing import process_image, resize_image, compress_image, add_watermark, resize_gif, compress_gif

logger = getLogger(__name__)

router = APIRouter()


@router.post("/resize/")
async def resize_image_endpoint(file: UploadFile = File(...), format: str = 'jpeg', new_width: int = None,
                                new_height: int = None):
    watermark = Image.open(WATERMARK_PATH)
    if format.lower() == 'gif':
        image_data = await file.read()
        resized_image_buf = await process_image(resize_gif, image_data, watermark, new_width, new_height)
    else:
        image = Image.open(io.BytesIO(await file.read()))
        resized_image_buf = await process_image(resize_image, image, watermark, format, new_width, new_height)
    return StreamingResponse(resized_image_buf, media_type=f"image/{format}")


@router.post("/compress/")
async def compress_image_endpoint(file: UploadFile = File(...), format: str = 'jpeg', quality: int = 75):
    watermark = Image.open(WATERMARK_PATH)
    if format.lower() == 'gif':
        image_data = await file.read()
        compressed_image_buf = await process_image(compress_gif, image_data, watermark, quality)
    else:
        image = Image.open(io.BytesIO(await file.read()))
        compressed_image_buf = await process_image(compress_image, image, watermark, quality)
    return StreamingResponse(compressed_image_buf, media_type=f"image/{format}")
