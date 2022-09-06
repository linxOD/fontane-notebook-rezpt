# XPath queries to search for min 1
XPATH = [
    ".//tei:sourceDoc//tei:note[@type='editorial']",
    ".//tei:sourceDoc//tei:note[@type='authorial']",
    ".//tei:sourceDoc//tei:surface",
    ".//tei:sourceDoc//tei:add",
    ".//tei:sourceDoc//tei:zone",
    ".//tei:sourceDoc//tei:line",
    ".//tei:sourceDoc//tei:seg",
    ".//tei:abstract",
    ".//tei:sourceDesc//tei:list[@type='editorial']/tei:item",
    ".//tei:sourceDesc//tei:list[@type='authorial']/tei:item",
    ".//tei:sourceDesc//tei:list[@type='Friedrich_Fontane']/tei:item",
    ".//tei:sourceDesc//tei:list[@type='Fontane_Blätter']/tei:item",
    ".//tei:sourceDoc//tei:rs",
    ".//tei:sourceDoc//tei:ptr",
    ".//tei:sourceDoc//tei:date",
    ".//tei:sourceDoc//tei:ref",
]
# added to filenames of processed data
FILENAME = "all"
# dir to save aggregated data download / serves as input to process data
IN_DIR = "notizbuecher"
# dir to save processed data
OUT_DIR = "notizbuecher_analyzed"
# REST API URL
URL = "https://fontane-nb.dariah.eu/rest/data"
# Namespaces for parsing XML docs
NSMAP = {
    'tei': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'exist': 'http://exist.sourceforge.net/NS/exist',
}
