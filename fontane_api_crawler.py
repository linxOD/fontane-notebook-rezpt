import requests
import lxml.etree as ET
import os
import glob
import jinja2
import pandas as pd
import json
import re

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
            # print(fn)
            if len(date) >= 1:
                date = tree.xpath(".//tei:creation/tei:date[@type='editorial']//tei:date/@when-iso", namespaces=self.nsmap)
            else:
                date = tree.xpath(".//tei:creation/tei:date[@type='editorial']/text()", namespaces=self.nsmap)
            date2 = tree.xpath(".//tei:creation/tei:date[@type='authorial']/text()", namespaces=self.nsmap)
            date3 = tree.xpath(".//tei:creation/tei:date[@type='Friedrich_Fontane']/text()", namespaces=self.nsmap)
            if "register" in title or "verzeichnis" in title or "Register" in title and "ODD" not in title:
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
                        "person": [],
                        "place": [],
                        "event": [],
                        "bibl": [],
                        "list": [],
                        "org": []
                    }
                    for e in rs:
                        if "tei:listPerson" in x:
                            idno = e.xpath("./tei:idno", namespaces=self.nsmap)
                            i_type = e.xpath("./tei:idno/@type", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            if idno:
                                pathObj["person"].append(
                                    {
                                        "type": i_type[0],
                                        "length": len(idno)
                                    }
                                )
                    for e in rs:
                        if "tei:listPlace" in x:
                            idno = e.xpath("./tei:idno", namespaces=self.nsmap)
                            i_type = e.xpath("./tei:idno/@type", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            if idno:
                                pathObj["place"].append(
                                    {
                                        "type": i_type[0],
                                        "length": len(idno)
                                    }
                                )
                    for e in rs:
                        if "tei:list/tei:list" in x:
                            idno = e.xpath("./tei:idno", namespaces=self.nsmap)
                            i_type = e.xpath("./tei:idno/@type", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            if idno:
                                pathObj["list"].append(
                                    {
                                        "type": i_type[0],
                                        "length": len(idno)
                                    }
                                )
                    for e in rs:
                        if "tei:listOrg" in x:
                            idno = e.xpath("./tei:idno", namespaces=self.nsmap)
                            i_type = e.xpath("./tei:idno/@type", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            if idno:
                                pathObj["org"].append(
                                    {
                                        "type": i_type[0],
                                        "length": len(idno)
                                    }
                                )
                    for e in rs:
                        if "tei:listBibl" in x:
                            idno = e.xpath("./tei:idno", namespaces=self.nsmap)
                            i_type = e.xpath("./tei:idno/@type", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            if idno:
                                pathObj["bibl"].append(
                                    {
                                        "type": i_type[0],
                                        "length": len(idno)
                                    }
                                )
                    for e in rs:
                        if "tei:listEvent" in x:
                            idno = e.xpath("./tei:idno", namespaces=self.nsmap)
                            i_type = e.xpath("./tei:idno/@type", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            if idno:
                                pathObj["event"].append(
                                    {
                                        "type": i_type[0],
                                        "length": len(idno)
                                    }
                                )
                    item["xpath"].append(pathObj)
                item["total_count"] = total_count
                notes.append(item)
                # print(pathObj)
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
                        "wrk": [],
                        "s_text": []
                    }
                    for e in rs:
                        if "tei:note" in x or "tei:list" in x:
                            text = e.xpath("normalize-space(.//text())", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            words = len(text.split())
                            if words > 4:
                                pathObj["wordcount"].append(words)
                        if "tei:abstract" in x:
                            text = e.xpath("normalize-space(.//tei:ab/text())", namespaces=self.nsmap)
                            # pathObj["context"].append(text)
                            words = len(text.split())
                            if words > 4:
                                pathObj["wordcount"].append(words)
                        if "tei:rs" in x:
                            el_type = e.xpath("@ref", namespaces=self.nsmap)[0]
                            if "eve:" in el_type:
                                pathObj["eve"].append(el_type)
                            if "org:" in el_type:
                                pathObj["org"].append(el_type)
                            if "plc:" in el_type:
                                pathObj["plc"].append(el_type)
                            if "psn:" in el_type:
                                pathObj["psn"].append(el_type)
                            if "wrk:" in el_type:
                                pathObj["wrk"].append(el_type)
                        if "tei:ptr" in x:
                            el_type = e.xpath("@target", namespaces=self.nsmap)[0]
                            if "lit:" in el_type:
                                pathObj["lit"].append(el_type)
                        if "tei:surface" in x:
                            s_text = e.xpath(".//text()", namespaces=self.nsmap)
                            # print(s_text)[0]
                            s_text = " ".join(s_text)
                            s_text = s_text.replace("\n", "")
                            s_text = s_text.replace("\t", "")
                            s_text = re.sub(r'[,.:;]', '', s_text, flags=re.MULTILINE)
                            # pathObj["s_text"].append(s_text)
                            s_word = s_text.split()
                            # print(s_word)[0]
                            sl_word = len(s_word)
                            pathObj["wordcount"].append(sl_word)
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
        # print(notes)
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
        template = templateEnv.get_template('./templates/index.j2')
        os.makedirs(os.path.join('out', 'html'), exist_ok=True)
        with open(os.path.join('out', 'html', 'index.html'), 'w') as f:
            f.write(template.render({"objects": data}))
        print(f"web app created: {os.path.join('out', 'html', 'index.html')}")
        return data

    def create_csv_data(self, data, filename):
        data = data
        table = []
        table1 = []
        table3 = []
        for x in data:
            if "register" in x["title"] or "verzeichnis" in x["title"] or "Register" in x["title"] and "ODD" not in x["title"]:
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
                    if i["person"]:
                        res = {}
                        for v in i["person"]:
                            if v["type"] in res:
                                res[v["type"]] += v["length"]
                            else:
                                res[v["type"]] = v["length"]
                    else:
                        res = 0
                    if i["place"]:
                        res_p = {}
                        for v in i["place"]:
                            if v["type"] in res_p:
                                res_p[v["type"]] += v["length"]
                            else:
                                res_p[v["type"]] = v["length"]
                    else:
                        res_p = 0
                    if i["event"]:
                        res_e = {}
                        for v in i["event"]:
                            if v["type"] in res_e:
                                res_e[v["type"]] += v["length"]
                            else:
                                res_e[v["type"]] = v["length"]
                    else:
                        res_e = 0
                    if i["list"]:
                        res_l = {}
                        for v in i["list"]:
                            if v["type"] in res_l:
                                res_l[v["type"]] += v["length"]
                            else:
                                res_l[v["type"]] = v["length"]
                    else:
                        res_l = 0
                    if i["bibl"]:
                        res_b = {}
                        for v in i["bibl"]:
                            if v["type"] in res_b:
                                res_b[v["type"]] += v["length"]
                            else:
                                res_b[v["type"]] = v["length"]
                    else:
                        res_b = 0
                    if i["org"]:
                        res_o = {}
                        for v in i["org"]:
                            if v["type"] in res_o:
                                res_o[v["type"]] += v["length"]
                            else:
                                res_o[v["type"]] = v["length"]
                    else:
                        res_o = 0
                    table3.append([x["filename"], x["title"], res, res_p, res_e, res_l, res_b, res_o, date, date2, date3, int(i["count"]), i["title"], round(int(average), 0)])
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
                        eve = "N/A"
                    if i["lit"]:
                        lit = i["lit"]
                    else:
                        lit = "N/A"
                    if i["org"]:
                        org = i["org"]
                    else:
                        org = "N/A"
                    if i["plc"]:
                        plc = i["plc"]
                    else:
                        plc = "N/A"
                    if i["psn"]:
                        psn = i["psn"]
                    else:
                        psn = "N/A"
                    if i["wrk"]:
                        wrk = i["wrk"]
                    else:
                        wrk = "N/A"
                    # if i["s_text"]:
                    #     s_text = " ".join(i["s_text"])
                    # else:
                    #     s_text = "N/A"
                    table.append([x["filename"], x["title"], eve, lit, org, plc, psn, wrk, date, date2, date3, int(i["count"]), i["title"], round(int(average), 0)])
            if "ODD" in x["title"]:
                for i in x["elementSpec"]:
                    table1.append([x["title"], "/".join(x["moduleRef"]), x["elementSpecLg"], i["ident"][0], "/".join(i["attDef"]), len(i["attDef"]), "/".join(i["valItem"]), len(i["valItem"])])
        df = pd.DataFrame(table, columns=['filename', 'notebook_title', 'eve', 'lit', 'org', 'plc', 'psn', 'wrk', 'date_e', 'date_a', 'date_f', 'count_context', 'context', 'average_context'])
        df.to_csv(os.path.join('out', self.out_dir, f"fonante_editorial_{filename}_notes.csv"), sep=",", encoding='utf-8', index=False)          
        print(f"table created: {os.path.join('out', self.out_dir, f'fonante_editorial_{filename}_notes.csv')}")
        df = pd.DataFrame(table1, columns=['title', 'modules', 'count_elements', 'el_ident', 'attDef', 'attDef_len', 'valItem', 'valItem_len'])
        df.to_csv(os.path.join('out', self.out_dir, f"fonante_editorial_{filename}_odd.csv"), sep=",", encoding='utf-8', index=False)
        print(f"table created: {os.path.join('out', self.out_dir, f'fonante_editorial_{filename}_odd.csv')}")
        df = pd.DataFrame(table3, columns=['filename', 'notebook_title', 'person', 'place', 'event', 'list', 'bibl', 'org', 'date_e', 'date_a', 'date_f', 'count_context', 'context', 'average_context'])
        df.to_csv(os.path.join('out', self.out_dir, f"fonante_editorial_{filename}_register.csv"), sep=",", encoding='utf-8', index=False)
        print(f"table created: {os.path.join('out', self.out_dir, f'fonante_editorial_{filename}_register.csv')}")
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
