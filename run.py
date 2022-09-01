from fontane_api_crawler import FtnAggDownload


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
fontane = FtnAggDownload(
    out_dir="./notizbuecher",
    url="https://fontane-nb.dariah.eu/rest/data"
)
