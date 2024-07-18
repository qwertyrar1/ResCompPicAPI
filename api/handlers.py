from logging import getLogger

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from settings import WATERMARK_PATH, IMAGE_FORMATS
from PIL import Image, UnidentifiedImageError
import io

from api.image_processing import process_image, resize_image, compress_image, resize_gif, compress_gif

logger = getLogger(__name__)

router = APIRouter()


@router.post("/resize/")
async def resize_image_endpoint(file: UploadFile = File(...), format: str = 'jpeg', new_width: int = None,
                                new_height: int = None):
    if format.lower() not in IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail='Incorrect Format')
    watermark = Image.open(WATERMARK_PATH)
    if format.lower() == 'gif':
        try:
            image_data = await file.read()
            resized_image_buf = await process_image(resize_gif, image_data, watermark, new_width, new_height)
        except UnidentifiedImageError as err:
            logger.error(err)
            raise HTTPException(status_code=400, detail="Incorrect File Format")
        except ValueError as err:
            logger.error(err)
            raise HTTPException(status_code=400, detail=f"Incorrect values: {err}")
    else:
        try:
            image = Image.open(io.BytesIO(await file.read()))
            resized_image_buf = await process_image(resize_image, image, watermark, format, new_width, new_height)
        except UnidentifiedImageError as err:
            logger.error(err)
            raise HTTPException(status_code=400, detail="Incorrect File Format")
        except ValueError as err:
            logger.error(err)
            raise HTTPException(status_code=400, detail=f"Incorrect values: {err}")
    return StreamingResponse(resized_image_buf, media_type=f"image/{format}")


@router.post("/compress/")
async def compress_image_endpoint(file: UploadFile = File(...), format: str = 'jpeg', quality: int = 75):
    if format.lower() not in IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail='Incorrect Format')
    watermark = Image.open(WATERMARK_PATH)
    if format.lower() == 'gif':
        try:
            image_data = await file.read()
            compressed_image_buf = await process_image(compress_gif, image_data, watermark, quality)
        except UnidentifiedImageError as err:
            logger.error(err)
            raise HTTPException(status_code=400, detail="Incorrect File Format")
    else:
        try:
            image = Image.open(io.BytesIO(await file.read()))
            compressed_image_buf = await process_image(compress_image, image, watermark, quality)
        except UnidentifiedImageError as err:
            logger.error(err)
            raise HTTPException(status_code=400, detail="Incorrect File Format")
    return StreamingResponse(compressed_image_buf, media_type=f"image/{format}")
