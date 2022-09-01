from fontane_api_crawler import FtnAnalyze
import os

xpath = [".//tei:sourceDoc//tei:note[@type='editorial']", 
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
         ".//tei:sourceDoc//tei:rs", ".//tei:sourceDoc//tei:date", 
         ".//tei:sourceDoc//tei:ref"
    ]
fn = "all"
fp = os.path.join('out', 'notizbuecher', 'tei_only', '*.xml')
fontane = FtnAnalyze(
    input_dir="notizbuecher",
    out_dir="notizbuecher_analyzed"
)

nodes = fontane.find_tei_elements(xpath, filename=fn, filepath=fp)
fontane.create_csv_data(data=nodes, filename=fn)
fontane.create_html_view(data=nodes)
