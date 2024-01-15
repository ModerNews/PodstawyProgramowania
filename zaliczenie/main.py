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
import enum
import os
import logging

import matplotlib.figure
import pandas as pd
import re
import docx2txt as docx  # pip install docx2txt
from odf import text, teletype
from odf.opendocument import load
import fitz as pdf  # pip install PyMuPDF
import charset_normalizer
import matplotlib.pyplot as plt


class FileMatch:
    def __init__(self, filename, string, reference):
        self.filename = filename
        self.string = string
        self.reference = reference


class MatchArray:
    def __init__(self, root_directory, search_string):
        self.root = root_directory
        self.search_string = search_string
        self.groups = []

    def __getitem__(self, item):
        return self.groups[item]

    def append(self, item):
        return self.groups.append(item)

    @property
    def files(self):
        return set([group.filename for group in self.groups])

    @property
    def match_strings(self):
        return set([group.string for group in self.groups])

    def matches_per_file(self):
        matches = {}
        for group in self.groups:
            if group.filename not in matches:
                matches[group.filename] = {}
            matches[group.filename][group.string] = matches[group.filename].get(group.string, 0) + 1
        return matches

    def matches_per_string(self):
        matches = {}
        for group in self.groups:
            matches[group.string] = matches.get(group.string, 0) + 1
        return matches

    def calculate_matches_per_file_dict(self):
        matches = self.matches_per_file()
        response = {}
        for file, hits in matches.items():
            for string in self.match_strings:
                response[string] = response.get(string, []) + [hits.get(string, 0.2)]
        return response

    def draw_matches_per_file_graph(self):
        matches = self.matches_per_file()
        bar_width = 1 / (len(self.match_strings) + 1)
        ax = plt.subplot(111)
        for j, items in enumerate((tmp := self.calculate_matches_per_file_dict()).items()):
            string, matches_arr = items
            ax.bar([base_pos + bar_width*(j + 0.5) for base_pos in range(len(matches_arr))], matches_arr, label=string, width=bar_width)
        plt.title(f"Strings that matched \"{self.search_string}\" query")
        plt.legend(fontsize=8)
        plt.grid(True, "major", "y")
        plt.ylabel("Number of found words")
        plt.yticks(range(0, max([max(file.values()) for file in matches.values()]) + 1))
        # TODO: Overlapping labels
        plt.xlabel("Files in which matches were found")
        plt.xticks([base_pos + bar_width*(len(self.match_strings)/2) for base_pos in range(len(matches_arr))], [os.path.relpath(path, self.root) for path in self.files], fontsize=8)

    def arr_to_csv(self):
        plt.figure(dpi=600)
        matches = self.calculate_matches_per_file_dict()
        arr = []
        for key, value in matches.items():
            arr.append([key] + value)
        return [[''] + [file.split("/")[-1] for file in self.files]] + arr

    def draw_match_table(self, ax):
        ax.table(cellText=self.arr_to_csv())


class Reference(enum.Enum):
    SENTENCE = "sentence"
    LINE = "line"


class Searcher:
    def __init__(self, root_directory, reference: Reference = Reference.LINE):
        self.dir = root_directory
        self.normalize: bool = True
        self.reference: Reference = reference

    def find_in_file(self, file_ctx, search):
        p = re.compile(search)
        return p.finditer(file_ctx)

    def find_sentence(self, file_ctx, search):
        """
        This regex is fucked
        Its point is to match sentences containing searched value
        :param file_ctx:
        :param search:
        :return:
        """
        p = re.compile(r"([^.]*?{}[^.]*[\.]?)".format(search))
        return p.finditer(file_ctx)

    def find_line(self, file_ctx, search):
        p = re.compile(fr'.*{search}.*\n?')
        return p.finditer(file_ctx)

    def find_reference(self, file_ctx, search: re.Match):
        if self.reference == Reference.LINE:
            reference_arr: list[re.Match] = self.find_line(file_ctx, search.group())
        elif self.reference == Reference.SENTENCE:
            reference_arr: list[re.Match] = self.find_sentence(file_ctx, search.group())
        else:
            raise AttributeError("Incorrect reference type")

        coordinate_arr = [((reference.start(), reference.end()), reference.group()) for reference in reference_arr]

        # TODO: implement more optimal search algorithm
        for i in range(len(coordinate_arr)):
            if coordinate_arr[i][0][0] <= search.start() <= coordinate_arr[i][0][1]:
                return coordinate_arr[i][1].replace("\n", " ")

    def match(self, search, *, regex: bool = True):
        findings = MatchArray(self.dir, search)
        tmp = os.walk(self.dir)
        if not regex:
            search = re.escape(search)
        for root, dirs, files in tmp:
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
                    try:
                        logging.debug(os.path.join(root, file))
                        doc = pdf.open(os.path.join(root, file))
                        doc = [page.get_text() for page in doc]
                        logging.debug(doc := "\n".join(doc))
                    except ValueError as e:
                        logging.warning(e)
                        doc = ""
                else:
                    logging.debug(os.path.join(root, file))
                    if not self.normalize:
                        try:
                            with open(os.path.join(root, file), 'r') as f:
                                doc = f.read()
                        except UnicodeDecodeError:
                            logging.warning("Could not match encoding for file " + str(os.path.join(root, file)))
                            doc = ""
                    else:
                        normalizer_file = charset_normalizer.from_path(os.path.join(root, file))
                        doc = str(normalizer_file.best())
                    logging.debug(doc)

                if tmp := self.find_in_file(doc, search):
                    # TODO: shits itself when there are multiple matches per reference
                    # for match in tmp:
                    #     findings.append(FileMatch(os.path.join(root, file), match, self.find_reference(doc, match)))
                    for m in tmp:
                        print(m.group(), m.start(), m.end())
                        findings.append(FileMatch(os.path.join(root, file), m.group(), self.find_reference(doc, m)))
        return findings


if __name__ == "__main__":
    root = "/home/gruzin/Downloads"
    # clue = "[Ww]nios"
    clue = "[Ii]mi[eę] [Ii] [Nn]azwisko"
    logging.basicConfig(level=logging.INFO)

    search = Searcher(root, Reference.SENTENCE)
    matches = search.match(clue)

    plt.figure(dpi=600)

    matches.draw_matches_per_file_graph()

    # ax = plt.subplot(222)
    # matches.draw_match_table(ax)

    # plt.show()
    plt.savefig("graph.png")

