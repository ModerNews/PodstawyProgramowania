"""
Należy opracować aplikację pozwalającą na wyszukiwanie danych w plikach zapisanych we wskazanej lokalizacji.
Aplikajca powinna pozwalać na wyszukiwanie danych w zawartości plików
(przynajmniej tekstowe txt+docx/odt, arkusze kalkulacyjne, pdf)
Aplikacja powinna posiadać ergonomiczny i funkcjonalny interfejs.
Aplikacja powinna umożliwiać generowane statystyk dotyczących wystąpień treści

na 5.5:
- wyszukiwanie obrazów po wpisaniu opisu
- web crawler
"""

import os
import logging
import pandas as pd
import re
import PySimpleGUI as sg
import docx2txt as docx  # pip install docx2txt
from odf import text, teletype
from odf.opendocument import load
import fitz as pdf  # pip install PyMuPDF

sg.theme('DarkAmber')

root = "/home/gruzin/Downloads"

logging.basicConfig(level=logging.DEBUG)


def find_in_file(file_ctx, search):
    return re.findall(search, file_ctx)  # using re for added regex availability


def find_sentence(file_ctx, search):
    """
    This regex is fucked
    Its point is to match sentences containing searched value
    :param file_ctx:
    :param search:
    :return:
    """
    return re.findall(r"([^.]*?{}[^.]*\.)".format(search), file_ctx)


clue = "[Ii]mię [Ii] [Nn]azwisko"
findings = []

tmp = os.walk(root)
for root, dirs, files in os.walk(root):
    for file in files:
        if "Dokument" in file:
            logging.debug("debug")
        if file.endswith(".docx"):
            logging.debug(os.path.join(root, file))
            doc = docx.process(os.path.join(root, file))
            logging.debug(doc)
        elif file.endswith(".odt"):
            logging.debug(os.path.join(root, file))
            doc = load(os.path.join(root, file))
            doc = [teletype.extractText(p) for p in doc.getElementsByType(text.P)]
            logging.debug(doc := "\n".join(doc))
        elif file.endswith(".pdf"):
            logging.debug(os.path.join(root, file))
            doc = pdf.open(os.path.join(root, file))
            doc = [page.get_text() for page in doc]
            logging.debug(doc := "\n".join(doc))
        elif file.endswith(".txt"):
            logging.debug(os.path.join(root, file))
            for encoding in ("utf-8", "cp1250"):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        doc = f.read()
                        break
                except UnicodeDecodeError:
                    continue
            logging.debug(doc)
        else:
            continue
        if tmp := find_in_file(doc, clue):
            findings.append((os.path.join(root, file), tmp))
            logging.info(tmp)

logging.info(findings)