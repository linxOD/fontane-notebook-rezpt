from fontane_api_crawler import FntNotebooks

fontane = FntNotebooks()
# fontane.save_tei_xml(save=False)
# fontane.get_real_tei()
# xpath = [".//tei:sourceDoc//tei:note[@type='editorial']", ".//tei:sourceDoc//tei:note[@type='authorial']", ".//tei:sourceDoc//tei:surface", ".//tei:sourceDoc//tei:add", ".//tei:sourceDoc//tei:zone", ".//tei:sourceDoc//tei:line", ".//tei:sourceDoc//tei:seg", ".//tei:abstract"]
# xpath = [".//tei:sourceDesc//tei:list[@type='editorial']/tei:item", ".//tei:sourceDesc//tei:list[@type='authorial']/tei:item", ".//tei:sourceDesc//tei:list[@type='Friedrich_Fontane']/tei:item", ".//tei:sourceDesc//tei:list[@type='Fontane_Blätter']/tei:item"]
xpath = [".//tei:sourceDoc//tei:rs"]
fn = "reference-string"
notes = fontane.find_tei_elements(xpath, dump=True, filename=fn)
fontane.create_csv_data(notes, filename=fn)
fontane.create_html_view(notes)
