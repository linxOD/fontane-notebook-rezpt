import requests
import lxml.etree as ET
import os
import glob
import jinja2
import pandas as pd


FONTANE_REST_URL = "https://fontane-nb.dariah.eu/rest/data"
DIR_TO_SAVE = "./notizbuecher"
NSMAP = {
    'tei': "http://www.tei-c.org/ns/1.0",
    'xml': "http://www.w3.org/XML/1998/namespace",
    'exist': 'http://exist.sourceforge.net/NS/exist',
}


class FntNotebooks():

    """class to download and save tei/xml of Fontane Notizbücher.
    https://fontane-nb.dariah.eu"""

    def get_rest_xml(self, url):
        "return eXistDB Rest overview xml"

        xml = requests.get(
            url
        )
        print(url)
        result = xml.text
        return result

    def parse_text_to_xml(self, save):
        "lxml xmlparser"

        data = self.get_rest_xml(self.url)
        parsed_data = ET.fromstring(data)
        if save:
            os.makedirs(self.save_dir, exist_ok=True)
            os.makedirs(os.path.join(self.save_dir, "main"), exist_ok=True)
            with open(os.path.join(self.save_dir, 'main', 'fontane_notizbücher_all.xml'), 'wb') as f:
                f.write(ET.tostring(parsed_data, pretty_print=True, encoding="utf-8"))
        return parsed_data

    def save_tei_xml(self, save):
        "download all Fontane Notizbücher TEI/XML"

        data = self.parse_text_to_xml(save=save)
        res = data.xpath(".//exist:resource", namespaces=self.nsmap)
        files = []
        for x in res:
            files.append(x.attrib["name"])
        for x in files:
            response = requests.get(
                os.path.join(self.url, x)
            )
            tei = response.text
            tree = ET.fromstring(tei)
            if save:
                with open(os.path.join(self.save_dir, x), 'wb') as f:
                    f.write(ET.tostring(tree, pretty_print=True, encoding="utf-8"))
                print(f"...saving {x}...")
        return files

    def get_real_tei(self):
        "filter for  TEI docs"

        files = {
            "tei": [],
            "none_tei": []
        }
        fn = glob.glob(os.path.join(self.save_dir, '*.xml'))
        for x in fn:
            with open(x, 'r') as f:
                data = f.read()
            tree = ET.fromstring(data)
            if tree.tag == "{http://www.tei-c.org/ns/1.0}TEI":
                files["tei"].append(tree)
                os.makedirs(os.path.join(self.save_dir, "tei_only"), exist_ok=True)
                with open(os.path.join(self.save_dir, "tei_only", x.split('/')[-1]), 'wb') as f:
                    f.write(ET.tostring(tree, pretty_print=True, encoding="utf-8"))
            else:
                files["none_tei"].append(tree)
                os.makedirs(os.path.join(self.save_dir, "none_tei"), exist_ok=True)
                with open(os.path.join(self.save_dir, "none_tei", x.split('/')[-1]), 'wb') as f:
                    f.write(ET.tostring(tree, pretty_print=True, encoding="utf-8"))
            os.remove(x)
        return files

    def find_tei_elements(self, xpath1, xpath2, dump):
        notes = []
        if dump:
            files = glob.glob(os.path.join(self.save_dir, 'tei_only', '*.xml'))
            for x in files:
                with open(x, "r") as f:
                    data = f.read()
                tree = ET.fromstring(data)
                title = tree.xpath(".//tei:title/text()", namespaces=self.nsmap)[0]
                editorial = tree.xpath(xpath1, namespaces=self.nsmap)
                pages = tree.xpath(xpath2, namespaces=self.nsmap)
                item = {
                    "title": title,
                    "notes": [],
                    "words": [],
                    "pages": [],
                    "p_words": [],
                }
                count_notes = 0
                count_pages = 0
                for e in editorial:
                    count_notes += 1
                    children = e.xpath(".//text()")
                    note = ' '.join(children)
                    item["notes"].append(note)
                    words = len(note.split(' '))
                    if words > 0:
                        item["words"].append(words)
                for p in pages:
                    count_pages += 1
                    children = p.xpath(".//text()")
                    page = ' '.join(children)
                    item["pages"].append(page)
                    words = len(page.split(' '))
                    if words > 0:
                        item["p_words"].append(words)
                item["count_notes"] = count_notes
                item["count_pages"] = count_pages
                notes.append(item)
        else:
            load = self.get_real_tei()
            data = load["tei"]
            for x in data:
                tree = x
                title = tree.xpath(".//tei:title/text()", namespaces=self.nsmap)[0]
                editorial = tree.xpath(xpath1, namespaces=self.nsmap)
                pages = tree.xpath(xpath2, namespaces=self.nsmap)
                item = {
                    "title": title,
                    "notes": [],
                    "words": [],
                    "pages": [],
                    "p_words": [],
                }
                count_notes = 0
                count_pages = 0
                for e in editorial:
                    count_notes += 1
                    children = e.xpath(".//text()")
                    note = ' '.join(children)
                    item["notes"].append(note)
                    words = len(note.split(' '))
                    if words > 0:
                        item["words"].append(words)
                for p in pages:
                    count_pages += 1
                    children = p.xpath(".//text()")
                    page = ' '.join(children)
                    item["pages"].append(page)
                    words = len(page.split(' '))
                    if words > 0:
                        item["p_words"].append(words)
                item["count_notes"] = count_notes
                item["count_pages"] = count_pages
                notes.append(item)
        return notes

    def create_html_view(self, data):
        data = data
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template('./templates/index.html')
        os.makedirs("html", exist_ok=True)
        with open('./html/index.html', 'w') as f:
            f.write(template.render({"objects": data}))
        return data

    def create_csv_data(self, data):
        data = data
        table = []
        for x in data:
            if "Notizbuch" in x["title"]:
                if x["words"]:
                    Sum = sum(x["words"])
                    Len = len(x["words"])
                    average = Sum / Len
                else:
                    average = 0
                if x["p_words"]:
                    Sum = sum(x["p_words"])
                    Len = len(x["p_words"])
                    p_average = Sum / Len
                else:
                    p_average = 0    
                table.append([x["title"], x["count_notes"], str(round(average, 2)), x["count_pages"], str(round(p_average, 2))])
        df = pd.DataFrame(table, columns=['notebook_title', 'no_of_editorial_notes', 'average_word_count', 'no_of_pages', 'avg_wordcount_pages'])
        df.to_csv("fonante_editorial_notes.csv", sep=",", encoding='utf-8', index=False)
        return data

    def __init__(
        self,
        url=FONTANE_REST_URL,
        out_dir=DIR_TO_SAVE,
        nsmap=NSMAP,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.url = url
        self.save_dir = out_dir
        self.nsmap = nsmap
