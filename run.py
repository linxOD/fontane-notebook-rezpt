from fontane_api_crawler import FtnAggDownload
from config import (
    IN_DIR, URL
)

fontane = FtnAggDownload(
    out_dir=IN_DIR,
    url=URL
)
