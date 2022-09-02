import requests
import lxml.etree as ET
import os
import glob
import jinja2
import pandas as pd
import json
from zipfile import ZipFile
from os.path import basename
from config import NSMAP


class FtnAggDownload():

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

    def parse_exist_xml(self):
        "lxml parser"

        data = self.get_rest_xml(self.url)
        parsed_data = ET.fromstring(data)
        os.makedirs('out', exist_ok=True)
        os.makedirs(os.path.join('out', self.save_dir), exist_ok=True)
        os.makedirs(os.path.join('out', self.save_dir, "main"), exist_ok=True)
        with open(os.path.join('out', self.save_dir, 'main', 'fontane_notizbuecher_all.xml'), 'wb') as f:
            f.write(ET.tostring(parsed_data, pretty_print=True, encoding="utf-8"))
        return parsed_data

    def save_tei_xml(self):
        "download all Fontane Notizbücher TEI/XML"

        data = self.parse_exist_xml()
        res = data.xpath(".//exist:resource", namespaces=self.nsmap)
        files = []
        for x in res:
            files.append(x.attrib["name"])
        for x in files:
            response = requests.get(
                os.path.join(self.url, x)
            )
            xml = response.text
            with open(os.path.join('out', self.save_dir, x), 'wb') as f:
                try:
                    tree = ET.fromstring(xml)
                    f.write(ET.tostring(tree, pretty_print=True, encoding="utf-8"))
                    print(f"...saving {x}...")
                except:
                    print(f"{x} could not be parsed and saved as xml.")
        return files

    def create_archive(self):
        os.makedirs(os.path.join('out', 'archive'), exist_ok=True)
        with ZipFile(os.path.join('out', 'archive', 'fontane-collection.zip'), 'w') as zipObj:
            for folderName, subfolders, filenames in os.walk(self.save_dir):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath, basename(filePath))
        return print(f"archive saved in {self.save_dir}")

    def get_real_tei(self):
        "filter for  TEI docs"

        files = {
            "tei": [],
            "none_tei": []
        }
        fn = glob.glob(os.path.join('out', self.save_dir, '*.xml'))
        for x in fn:
            with open(x, 'r') as f:
                data = f.read()
            tree = ET.fromstring(data)
            if tree.tag == "{http://www.tei-c.org/ns/1.0}TEI":
                files["tei"].append(tree)
                os.makedirs(os.path.join('out', self.save_dir, "tei_only"), exist_ok=True)
                with open(os.path.join('out', self.save_dir, "tei_only", x.split('/')[-1]), 'wb') as f:
                    f.write(ET.tostring(tree, pretty_print=True, encoding="utf-8"))
            else:
                files["none_tei"].append(tree)
                os.makedirs(os.path.join('out', self.save_dir, "none_tei"), exist_ok=True)
                with open(os.path.join('out', self.save_dir, "none_tei", x.split('/')[-1]), 'wb') as f:
                    f.write(ET.tostring(tree, pretty_print=True, encoding="utf-8"))
            os.remove(x)
        return files

    def __init__(
        self,
        url=None,
        out_dir=None,
        nsmap=NSMAP,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.url = url
        self.save_dir = out_dir
        self.nsmap = nsmap
        self.save = self.save_tei_xml()
        self.archive = self.create_archive()
        self.tei = self.get_real_tei()


class FtnAnalyze():
    
    "process and analyze Fontane Notebook TEI data"

    def find_tei_elements(self, xpath, filename, filepath):
        notes = []
        data = glob.glob(filepath)
        for x in data:
            if type(x) == str:
                with open(x, "r") as f:
                    data = f.read()
                tree = ET.fromstring(data)
            else:
                tree = x
            fn = basename(x).replace(".xml", "")
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
                    "filename": fn,
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
                        text = e.xpath("normalize-space(.//text())")
                        if "tei:note" in x or "tei:abstract" in x or "tei:list" in x:
                            pathObj["context"].append(text)
                            words = len(text.split())
                        else:
                            words = 0
                        pathObj["wordcount"].append(words)
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
        os.makedirs(os.path.join('out', self.out_dir), exist_ok=True)
        with open(os.path.join('out', self.out_dir, f"{filename}.json"), "w") as f:
            json.dump(notes, f)
        print(f"all TEI files proccessed and serialized in JSON")
        print(f"JSON dump created in /out/{self.out_dir}/{filename}.json")
        return notes

    def create_html_view(self, data):
        data = data
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)
        template = templateEnv.get_template('./templates/index.html')
        os.makedirs(os.path.join('out', 'html'), exist_ok=True)
        with open(os.path.join('out', 'html', 'index.html'), 'w') as f:
            f.write(template.render({"objects": data}))
        print(f"web app created: {os.path.join('out', 'html', 'index.html')}")
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
        df.to_csv(os.path.join('out', self.out_dir, f"fonante_editorial_{filename}_notes.csv"), sep=",", encoding='utf-8', index=False)          
        print(f"table created: {os.path.join('out', self.out_dir, f'fonante_editorial_{filename}_notes.csv')}")
        df = pd.DataFrame(table1, columns=['title', 'modules', 'count_elements', 'el_ident', 'attDef', 'attDef_len', 'valItem', 'valItem_len'])
        df.to_csv(os.path.join('out', self.out_dir, f"fonante_editorial_{filename}_odd.csv"), sep=",", encoding='utf-8', index=False)
        print(f"table created: {os.path.join('out', self.out_dir, f'fonante_editorial_{filename}_odd.csv')}")
        return data
    
    def __init__(
        self,
        input_dir=None,
        out_dir=None,
        nsmap=NSMAP,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.out_dir = out_dir
        self.input_dir = input_dir
        self.nsmap = nsmap
