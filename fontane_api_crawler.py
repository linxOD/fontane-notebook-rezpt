import requests
import lxml.etree as ET
import os
import glob
import jinja2
import pandas as pd
import json


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

    def find_tei_elements(self, xpath, dump, filename):
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
            filename = os.path.basename(x).replace(".xml", "")
            title = tree.xpath(".//tei:title/text()", namespaces=self.nsmap)[0]
            date = tree.xpath(".//tei:creation/tei:date[@type='editorial']//tei:date/@when-iso", namespaces=self.nsmap)
            if len(date) >= 1:
                date = tree.xpath(".//tei:creation/tei:date[@type='editorial']//tei:date/@when-iso", namespaces=self.nsmap)
            else:
                date = tree.xpath(".//tei:creation/tei:date[@type='editorial']/text()", namespaces=self.nsmap)
            date2 = tree.xpath(".//tei:creation/tei:date[@type='authorial']/text()", namespaces=self.nsmap)
            date3 = tree.xpath(".//tei:creation/tei:date[@type='Friedrich_Fontane']/text()", namespaces=self.nsmap)
            if "Notizbuch" in title:
                item = {
                    "filename": filename,
                    "title": title,
                    "date_e": date,
                    "date_a": date2,
                    "date_f": date3,
                    "xpath": []
                }
                total_count = 0;
                for x in xpath:
                    rs = tree.xpath(x, namespaces=self.nsmap)
                    total_count += len(rs)
                    
                    pathObj = {
                        "title": x,
                        "context": [],
                        "wordcount": [],
                        "count": len(rs),
                        "eve": [],
                        "lit": [],
                        "org": [],
                        "plc": [],
                        "psn": [],
                        "wrk": []
                    }
                    for e in rs:
                        if "tei:rs" in x:
                            el_type = e.xpath("@ref")[0]
                            if "eve:" in el_type:
                                pathObj["eve"].append(" ".join(el_type))
                            if "lit:" in el_type:
                                pathObj["lit"].append(" ".join(el_type))
                            if "org:" in el_type:
                                pathObj["org"].append(" ".join(el_type))
                            if "plc:" in el_type:
                                pathObj["plc"].append(" ".join(el_type))
                            if "psn:" in el_type:
                                pathObj["psn"].append(" ".join(el_type))
                            if "wrk:" in el_type:
                                pathObj["wrk"].append(" ".join(el_type))
                        children = e.xpath(".//text()")
                        note = ' '.join(children)
                        if "tei:note" in x or "tei:abstract" in x or "tei:list" in x:
                            note = note.replace("\n", "")
                            note = note.replace("  ", "")
                            pathObj["context"].append(note)
                            words = len(note.split(' '))
                        else:
                            words = 0
                        if words > 0:
                            pathObj["wordcount"].append(words)
                    pathObj["eve"] = len(pathObj["eve"])
                    pathObj["lit"] = len(pathObj["lit"])
                    pathObj["org"] = len(pathObj["org"])
                    pathObj["plc"] = len(pathObj["plc"])
                    pathObj["psn"] = len(pathObj["psn"])
                    pathObj["wrk"] = len(pathObj["wrk"])
                    item["xpath"].append(pathObj)
                item["total_count"] = total_count
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
        with open(f"{filename}.json", "w") as f:
            json.dump(notes, f)
        print(notes)
        return notes

    def create_html_view(self, data):
        data = data
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)
        template = templateEnv.get_template('./templates/index.html')
        os.makedirs("html", exist_ok=True)
        with open('./html/index.html', 'w') as f:
            f.write(template.render({"objects": data}))
        return data

    def create_csv_data(self, data, filename):
        data = data
        table = []
        table1 = []
        for x in data:
            if "Notizbuch" in x["title"]:
                if x["date_e"]:
                    date = " ".join(x["date_e"])
                    date = date.replace("\n", "")
                    date = date.replace("  ", "")
                else: 
                    date = ""
                if x["date_a"]:
                    date2 = " ".join(x["date_a"])
                else: 
                    date2 = ""
                if x["date_f"]:
                    date3 = " ".join(x["date_f"])
                else: 
                    date3 = ""
                for i in x["xpath"]:
                    if i["wordcount"]:
                        Sum = sum(i["wordcount"])
                        Len = len(i["wordcount"])
                        average = Sum / Len
                    else:
                        average = 0
                    if i["eve"]:
                        eve = i["eve"]
                    else:
                        eve = 0
                    if i["lit"]:
                        lit = i["lit"]
                    else:
                        lit = 0
                    if i["org"]:
                        org = i["org"]
                    else:
                        org = 0
                    if i["plc"]:
                        plc = i["plc"]
                    else:
                        plc = 0
                    if i["psn"]:
                        psn = i["psn"]
                    else:
                        psn = 0
                    if i["wrk"]:
                        wrk = i["wrk"]
                    else:
                        wrk = 0
                    table.append([x["filename"], x["title"], eve, lit, org, plc, psn, wrk, date, date2, date3, i["count"], i["title"], int(round(average, 0))])
            if "ODD" in x["title"]:
                for i in x["elementSpec"]:
                    table1.append([x["title"], "/".join(x["moduleRef"]), x["elementSpecLg"], i["ident"][0], "/".join(i["attDef"]), len(i["attDef"]), "/".join(i["valItem"]), len(i["valItem"])])
        df = pd.DataFrame(table, columns=['filename', 'notebook_title', 'eve', 'lit', 'org', 'plc', 'psn', 'wrk', 'date_e', 'date_a', 'date_f', 'count_context', 'context', 'average_context'])
        df.to_csv(f"fonante_editorial_{filename}_notes.csv", sep=",", encoding='utf-8', index=False)          
        df = pd.DataFrame(table1, columns=['title', 'modules', 'count_elements', 'el_ident', 'attDef', 'attDef_len', 'valItem', 'valItem_len'])
        df.to_csv(f"fonante_editorial_{filename}_odd.csv", sep=",", encoding='utf-8', index=False)
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
