from PIL import Image, ImageSequence
import io
import numpy as np


def resize_image(image: Image, new_width=None, new_height=None) -> Image.Image:
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

    resized_image = image.resize(resized_dimensions, Image.LANCZOS)
    return resized_image


def resize_gif(image: Image, new_width=None, new_height=None):
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
    frames = list(_thumbnail_frames(image, resized_dimensions))
    buf = io.BytesIO()
    output_image = frames[0]
    output_image.save(
        buf,
        save_all=True,
        append_images=frames[1:],
        format='gif'
    )
    buf.seek(0)
    return buf


def _thumbnail_frames(image, max_size):
    for frame in ImageSequence.Iterator(image):
        new_frame = frame.copy()
        new_frame.thumbnail(max_size, Image.Resampling.LANCZOS)
        yield new_frame


def _compress_frames(image, quality):
    for frame in ImageSequence.Iterator(image):
        frame_rgb = frame.convert('RGB')
        buf = io.BytesIO()
        frame_rgb.save(buf, quality=quality, format='JPEG')
        buf.seek(0)
        frame_compressed = Image.open(buf).convert('P', palette=Image.ADAPTIVE)
        yield frame_compressed


def _add_watermark_frames(image, watermark, position: tuple):
    for frame in ImageSequence.Iterator(image):
        res = frame.copy().convert('RGBA')
        watermark = watermark.convert('RGBA')

        x = np.asarray(watermark).copy()
        x[:, :, 3] = (100 * (np.sum(x[:, :, :3], axis=2) < 700)).astype(np.uint8)
        watermark = Image.fromarray(x)

        alpha = watermark.getchannel('A')
        crop = alpha.getbbox()
        watermark = watermark.crop(crop)

        res.alpha_composite(watermark, position)
        rgb_res = res.convert('RGB')

        buf = io.BytesIO()
        rgb_res.save(buf, format='JPEG')
        buf.seek(0)

        frame_watermarked = Image.open(buf).convert('P', palette=Image.ADAPTIVE)
        yield frame_watermarked


def compress_image(image: Image, quality: int, format: str) -> Image.Image:
    buf = io.BytesIO()
    image.save(buf, format=format, quality=quality)
    buf.seek(0)
    return Image.open(buf)


def compress_gif(image: Image, quality: int, format: str):
    frames = list(_compress_frames(image, quality))
    buf = io.BytesIO()
    output_image = frames[0]
    output_image.save(
        buf,
        save_all=True,
        append_images=frames[1:],
        format=format
    )
    buf.seek(0)
    return buf


def add_watermark(image, watermark, position: tuple) -> Image.Image:
    res = image.copy().convert('RGBA')
    watermark = watermark.convert('RGBA')

    x = np.asarray(watermark).copy()
    x[:, :, 3] = (100 * (np.sum(x[:, :, :3], axis=2) < 700)).astype(np.uint8)
    watermark = Image.fromarray(x)

    alpha = watermark.getchannel('A')
    crop = alpha.getbbox()
    watermark = watermark.crop(crop)

    res.alpha_composite(watermark, position)

    return res


def add_watermark_gif(image, watermark, position: tuple):
    frames = list(_add_watermark_frames(image, watermark, position))
    buf = io.BytesIO()
    output_image = frames[0]
    output_image.save(
        buf,
        save_all=True,
        append_images=frames[1:],
        format='gif'
    )
    buf.seek(0)
    return buf

