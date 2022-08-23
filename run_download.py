from fontane_api_crawler import FntNotebooks

fontane = FntNotebooks()
# fontane.save_tei_xml(save=False)
# fontane.get_real_tei()
xpath = [".//tei:note[@type='editorial']", ".//tei:sourceDoc/tei:surface"]
notes = fontane.find_tei_elements(xpath, dump=True)
fontane.create_csv_data(notes)
fontane.create_html_view(notes)
print(notes)
