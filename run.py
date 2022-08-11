from fontane_api_crawler import FntNotebooks

fontane = FntNotebooks()
fontane.save_tei_xml(save=True)
fontane.get_real_tei()
notes = fontane.find_tei_elements(".//tei:note[@type='editorial']")
fontane.create_csv_data(notes)
fontane.create_html_view(notes)
