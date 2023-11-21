import functools
import io
import httpx
import numpy as np
import os
import sys

from io import BytesIO
from PIL import Image, ImageDraw


MASK_CIRCULAR = "./img/mask_circular.png"

cache = {}

def memoize(func):
    global cache

    def wrapper(*args):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result

    return wrapper


def async_memoize():
    global cache

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args):
            if args in cache:
                return cache[args]
            else:
                result = await func(*args)
                cache[args] = result
                return result

        return wrapped

    return wrapper


@memoize
def load_img(path):
    if getattr(sys, 'frozen', False):
        image = Image.open(os.path.join(sys._MEIPASS, path))
    else:
        image = Image.open(path)
    
    return image

@memoize
def load_img_from_url(url) -> Image.Image:
    img_data = httpx.get(url).content
    return Image.open(io.BytesIO(img_data)).convert("RGBA")


@async_memoize()
async def async_load_img_from_url(url) -> Image.Image:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

        return Image.open(BytesIO(resp.content))

    return None


def cropping_image_in_a_circular(img: Image.Image) -> Image.Image:
    mask_ = load_img(MASK_CIRCULAR).convert('L')
    mask_ = mask_.resize(img.size)
    return cropping_image_mask(img, mask_)


def cropping_image_mask(img: Image.Image, mask: Image.Image) -> Image.Image:
    background = Image.new("RGBA", img.size, (0, 0, 0, 0))
    new_img = Image.composite(img, background, mask)
    return new_img


def cropping_image_in_a_rounded_rectangle(img: Image.Image, radius=10) -> Image.Image:
    mask = Image.new("L", img.size, "black")
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), fill="white", radius=radius)

    img = cropping_image_mask(img, mask)
    return img


def remove_background(img: Image.Image) -> Image.Image:
    img = img.convert('RGBA')

    data = np.array(img)
    # just use the rgb values for comparison
    rgb = data[:, :, :3]
    color = [0, 0, 0]  # Original value
    black = [0, 0, 0, 0]
    mask = np.all(rgb == color, axis=-1)
    # change all pixels that match color to white
    data[mask] = black

    return Image.fromarray(data)


def open_gif_image(path) -> list[Image.Image]:
    img = []
    with load_img(path) as im:

        try:
            while 1:
                img.append(im.copy())
                im.seek(im.tell() + 1)
        except EOFError:

            pass  # end of sequence

    return img
