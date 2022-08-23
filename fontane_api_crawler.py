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

    def find_tei_elements(self, xpath, dump):
        notes = []
        if dump:
            data = glob.glob(os.path.join(self.save_dir, 'tei_only', '*.xml'))
        else:
            load = self.get_real_tei()
            data = load["tei"]
        for x in data:
            if type(x) == str:
                with open(x, "r") as f:
                    data = f.read()
                tree = ET.fromstring(data)
            else:
                tree = x
            title = tree.xpath(".//tei:title/text()", namespaces=self.nsmap)[0]
            if "Notizbuch" in title:
                item = {
                    "title": title,
                    "xpath": []
                }
                for x in xpath:
                    rs = tree.xpath(x, namespaces=self.nsmap)
                    pathObj = {
                        "title": x,
                        "context": [],
                        "wordcount": [],
                        "count": len(rs)
                    }
                    for e in rs:
                        children = e.xpath(".//text()")
                        note = ' '.join(children)
                        # pathObj["context"].append(note)
                        words = len(note.split(' '))
                        if words > 0:
                            pathObj["wordcount"].append(words)
                    item["xpath"].append(pathObj)
                notes.append(item)
            if "ODD" in title:
                item = {
                    "title": title,
                    "elementSpec": []
                }
                moduleRef = tree.xpath(".//tei:moduleRef/@key", namespaces=self.nsmap)
                item["moduleRef"] = moduleRef
                elementSpec = tree.xpath(".//tei:elementSpec", namespaces=self.nsmap)
                for x in elementSpec:
                    el = {
                        "ident": x.xpath("./@ident", namespaces=self.nsmap),
                        "attDef": x.xpath("./tei:attList/tei:attDef/@ident", namespaces=self.nsmap),
                        "valItem": x.xpath("./tei:attList/tei:attDef/tei:valList/tei:valItem/@ident", namespaces=self.nsmap),
                    }
                    item["elementSpec"].append(el)
                item["elementSpecLg"] = len(elementSpec)
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
        table1 = []
        for x in data:
            if "Notizbuch" in x["title"]:
                for i in x["xpath"]:
                    if i["wordcount"]:
                        Sum = sum(i["wordcount"])
                        Len = len(i["wordcount"])
                        average = Sum / Len
                    else:
                        average = 0
                    table.append([x["title"], i["count"], i["title"], str(round(average, 2))])
            if "ODD" in x["title"]:
                for i in x["elementSpec"]:
                    table1.append([x["title"], "/".join(x["moduleRef"]), x["elementSpecLg"], i["ident"][0], "/".join(i["attDef"]), len(i["attDef"]), "/".join(i["valItem"]), len(i["valItem"])])
        df = pd.DataFrame(table, columns=['notebook_title', 'count_context', 'context', 'average_context'])
        df.to_csv("fonante_editorial_notes.csv", sep=",", encoding='utf-8', index=False)          
        df = pd.DataFrame(table1, columns=['title', 'modules', 'count_elements', 'el_ident', 'attDef', 'attDef_len', 'valItem', 'valItem_len'])
        df.to_csv("fonante_editorial_odd.csv", sep=",", encoding='utf-8', index=False)
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
