from PIL import Image, ImageSequence
import io
import numpy as np

from concurrent.futures import ProcessPoolExecutor
import asyncio

executor = ProcessPoolExecutor()


async def process_image(func, *args):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, func, *args)
    return result


def _thumbnail_frames(image: Image, watermark: Image, max_size: tuple):
    for frame in ImageSequence.Iterator(image):
        new_frame = frame.copy()
        new_frame = add_watermark(new_frame, watermark)
        new_frame.thumbnail(max_size, Image.Resampling.LANCZOS)
        yield new_frame


def _add_watermark_frames(image: Image, watermark: Image, quality: int = 95):
    for frame in ImageSequence.Iterator(image):
        res = frame.copy().convert('RGBA')
        watermark = watermark.convert('RGBA')

        x = np.asarray(watermark).copy()
        x[:, :, 3] = (100 * (np.sum(x[:, :, :3], axis=2) < 700)).astype(np.uint8)
        watermark = Image.fromarray(x)

        alpha = watermark.getchannel('A')
        crop = alpha.getbbox()
        watermark = watermark.crop(crop)

        res.alpha_composite(watermark, (10, 10))
        rgb_res = res.convert('RGB')

        buf = io.BytesIO()
        rgb_res.save(buf, format='JPEG', quality=quality)
        buf.seek(0)

        frame_watermarked = Image.open(buf).convert('P', palette=Image.ADAPTIVE)
        yield frame_watermarked


def resize_image(image: Image, watermark: Image, format: str, new_width: int = None,
                 new_height: int = None) -> io.BytesIO:
    original_width, original_height = image.size

    if new_width and new_height:
        resized_dimensions = (new_width, new_height)
    elif new_width:
        width_percent = new_width / float(original_width)
        new_height = int((float(original_height) * float(width_percent)))
        resized_dimensions = (new_width, new_height)
    elif new_height:
        height_percent = new_height / float(original_height)
        new_width = int((float(original_width) * float(height_percent)))
        resized_dimensions = (new_width, new_height)
    else:
        resized_dimensions = (original_width, original_height)
    image = add_watermark(image, watermark)
    resized_image = image.resize(resized_dimensions, Image.LANCZOS)
    buf = io.BytesIO()
    resized_image.save(buf, format=format)
    buf.seek(0)
    return buf


def resize_gif(data: bytes, watermark: Image, new_width: int = None, new_height: int = None) -> io.BytesIO:
    image = Image.open(io.BytesIO(data))
    original_width, original_height = image.size

    if new_width and new_height:
        resized_dimensions = (new_width, new_height)
    elif new_width:
        width_percent = new_width / float(original_width)
        new_height = int((float(original_height) * float(width_percent)))
        resized_dimensions = (new_width, new_height)
    elif new_height:
        height_percent = new_height / float(original_height)
        new_width = int((float(original_width) * float(height_percent)))
        resized_dimensions = (new_width, new_height)
    else:
        resized_dimensions = (original_width, original_height)
    frames = list(_thumbnail_frames(image, watermark, resized_dimensions))
    buf = io.BytesIO()
    output_image = frames[0]
    output_image.save(
        buf,
        save_all=True,
        append_images=frames[1:],
        format='GIF',
        loop=0
    )
    buf.seek(0)
    return buf


def compress_image(image: Image, watermark: Image, quality: int) -> io.BytesIO:
    image = add_watermark(image, watermark)
    buf = io.BytesIO()
    image.save(buf, format='JPEG', quality=quality)
    buf.seek(0)
    return buf


def compress_gif(data: bytes, watermark: Image, quality: int) -> io.BytesIO:
    image = Image.open(io.BytesIO(data))
    frames = list(_add_watermark_frames(image, watermark, quality))
    buf = io.BytesIO()
    output_image = frames[0]
    output_image.save(
        buf,
        save_all=True,
        append_images=frames[1:],
        format='GIF',
        loop=0
    )
    buf.seek(0)
    return buf


def add_watermark(image: Image, watermark: Image) -> Image.Image:
    res = image.copy().convert('RGBA')
    watermark = watermark.convert('RGBA')

    x = np.asarray(watermark).copy()
    x[:, :, 3] = (100 * (np.sum(x[:, :, :3], axis=2) < 700)).astype(np.uint8)
    watermark = Image.fromarray(x)

    alpha = watermark.getchannel('A')
    crop = alpha.getbbox()
    watermark = watermark.crop(crop)

    res.alpha_composite(watermark, (10, 10))
    rgb_res = res.convert('RGB')

    return rgb_res
