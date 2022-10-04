from fontane_api_crawler import FtnAnalyze
import os

from config import (
    XPATH, FILENAME, IN_DIR, OUT_DIR
)

fontane = FtnAnalyze(
    input_dir=IN_DIR,
    out_dir=OUT_DIR
)
fp = os.path.join('out', IN_DIR, 'tei_only', '*.xml')
nodes = fontane.find_tei_elements(xpath=XPATH, filename=FILENAME, filepath=fp)
fontane.create_csv_data(data=nodes, filename=FILENAME)
fontane.create_html_view(data=nodes)
