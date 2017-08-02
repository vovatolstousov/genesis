from PIL import Image


def resize_photo(instance, width, height, filename, max_thumbnail_size):
    """
    Resize model photo to needed sizes.
    """
    if width and height:

        max_size = max(width, height)

        if max_size > max_thumbnail_size:
            image = Image.open(filename)
            image = image.resize(
                (round(width / max_size * max_thumbnail_size),
                 round(height / max_size * max_thumbnail_size)),
                Image.ANTIALIAS
            )
            image.save(filename)

