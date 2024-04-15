from __future__ import annotations

from palet.pallet import Pallet, ConversionPallet
from palet.color import Color

from PIL import Image, ImageDraw, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


def extract_pallet(f: str) -> Pallet:
    image = Image.open(f)
    image = image.convert("RGBA")

    color_list = image.getcolors()
    if color_list is None:
        raise ValueError(
            f'Extracted Pallet is NoneType. Use alternative `{extract_pallet_ext.__name__}` to extract all instead.'
        )

    new_pallet = Pallet(*(x[-1] for x in color_list))
    return new_pallet


def extract_pallet_ext(f: str, alpha_threshold=0) -> Pallet:
    image = Image.open(f)
    image = image.convert("RGBA")

    new_pallet = Pallet()
    for pix in image.getdata():
        if pix[-1] > alpha_threshold:
            new_pallet.add(pix)

    return new_pallet


def export_pallet(pallet, f, size=(8, 8)) -> None:
    f_image = Image.new("RGBA", (size[0] * len(pallet), size[1]), 0)
    draw = ImageDraw.Draw(f_image)

    for i, color in enumerate(pallet):
        if isinstance(color, Color):
            draw.rectangle(((i * size[0], 0), ((i + 1) * size[0], size[1])), color.irgba)
        else:
            draw.rectangle(((i * size[0], 0), ((i + 1) * size[0], size[1])), color)

    f_image.save(f)
    return


def convert_pallet(f_in, cmap: ConversionPallet | dict = None, f_out="") -> None:
    if cmap is None:
        return

    if isinstance(cmap, ConversionPallet):
        cmap = cmap.to_dict()

    f_image = Image.open(f_in)
    f_image = f_image.convert("RGBA")

    new_image = Image.new("RGBA", f_image.size)
    for x in range(f_image.width):
        for y in range(f_image.height):
            pix = f_image.getpixel((x, y))

            if pix in cmap:
                new_pix = cmap[pix]
            else:
                new_pix = pix
            new_image.putpixel((x, y), new_pix)

    f_out = f_out if f_out != "" else f_in
    new_image.save(f_out)
    return


def extract_convert_pallet(f_a: str, f_b: str, f_out="", method="min_distance") -> None:
    pa = extract_pallet_ext(f_a)
    pb = extract_pallet_ext(f_b)

    if method == "min_distance":
        cmap = ConversionPallet.map(pa, pb)
    else:
        raise NotImplemented(f"Unable to run {extract_convert_pallet.__name__} with method `{method}`.")

    convert_pallet(f_a, cmap, f_out=f_out)
    return
