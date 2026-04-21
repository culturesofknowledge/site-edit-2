import re
from urllib.parse import urlparse

from django import template

register = template.Library()

# Common image file extensions
_IMAGE_EXT_PATTERN = re.compile(r'\.(jpe?g|png|gif|bmp|svg|webp|tiff?|ico)(\?.*)?$', re.IGNORECASE)


def _is_direct_image_url(url: str) -> bool:
    """Return True if the URL is likely to serve an image directly."""
    if not url:
        return False
    # Local media files are always servable as images
    if url.startswith('/media/') or url.startswith('/static/'):
        return True
    # For external URLs, check only the path (strip fragment and query)
    parsed = urlparse(url)
    path = parsed.path
    if _IMAGE_EXT_PATTERN.search(path):
        return True
    return False


@register.simple_tag
def thumbnail_url(image_filename):
    """Return the URL to use as thumbnail src, or empty string if not a direct image."""
    if _is_direct_image_url(image_filename):
        return image_filename
    return ''
