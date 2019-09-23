import os
from bs4 import BeautifulSoup
import json

"""
metadata data structure:
{
    "title": Str,
    "author": List[Str],
    "institute": List[Str],
    "mail": List[Str],
    "journal": Str，
    "outline": {
    "Abstract":Str,
    "Introduction": Str,
    ....
    "References":Str
    }
    "Abstract":List[Str],
}
"""

"""
content data structure:
{
    
    "Introduction": List[Str],
    ...
    "References":List[Str]
    "Tables":List[List[List]]
}
"""


class Extractor(object):
    def __init__(self, path, file):

        self.title = []
        self.author = []
        self.institute = []
        self.abstract = []
        self.outline = []
        self.journal = ''
        self.path = path
        self.file = file
        self.has_metadata = False
        self.has_content = False
        self.content = []

    def parse_page(self, soup):
        pgs = soup.find_all(['p', 'h', 'h1', 'h2', 'h3', 'h4', 'h5'])
        j = 0
        while self.title == [] and j < len(pgs):
            if 'h' in pgs[j].name:
                self.title.append(pgs[j].text)
                h = pgs[j].name
                j += 1
                while j < len(pgs) and pgs[j].name == h:
                    self.title.append(pgs[j].text)
                    j += 1
            j += 1

        while self.abstract == [] and j < len(pgs):
            if pgs[j].text.lower().strip().startswith('abstract'):
                j += 1
                end = True
                while j < len(pgs) and pgs[j].name == 'p':
                    if 'style' in pgs[j].attrs:
                        if 'text-align: justify' in pgs[j].attrs['style']:
                            text = pgs[j].text.strip()
                            if text == '':
                                j += 1
                                continue
                            if end:
                                self.abstract.append(text)
                            else:
                                self.abstract[-1] += ' ' + text

                            if text[-1] not in ['.', ':', '!', '?', '。', '！', '？']:
                                end = False
                            else:
                                self.abstract[-1] = ' '.join(self.abstract[-1].replace('- ', '').split())
                                end = True

                        elif 'text-align: left' in pgs[j].attrs['style']:
                            text = pgs[j].text.strip()
                            if len(text.split()) < 60:
                                j += 1
                                continue
                            if end:
                                self.abstract.append(text)
                            else:
                                self.abstract[-1] += ' ' + text

                            if text[-1] not in ['.', ':', '!', '?', '。', '！', '？']:
                                end = False
                            else:
                                self.abstract[-1] = ' '.join(self.abstract[-1].replace('- ', '').split())
                                end = True

                    j += 1
                if not end:
                    self.abstract[-1] = ' '.join(self.abstract[-1].replace('- ', '').split())

                break

            if 'h' in pgs[j].name:
                tmp = []
                for c in pgs[j].contents:
                    try:
                        str = c.text.replace(',', '')
                        str = str.replace('and', '')
                        str = str.strip()
                        if str != '':
                            tmp.append(str)
                    except:
                        str = c.replace(',', '')
                        str = str.replace('and', '')
                        str = str.strip()
                        if str != '':
                            tmp.append(str)
                if tmp != []:
                    self.author.append(tmp)

            elif 'style' in pgs[j].attrs:
                tmp = []
                for c in pgs[j].contents:
                    try:
                        str = c.text.strip()
                        if str != '':
                            tmp.append(str)
                    except:
                        str = c.strip()
                        if str != '':
                            tmp.append(str)
                if tmp != []:
                    self.institute.append(tmp)
            j += 1

    def get_metadata(self):
        """Extract title, author, institute, outline, abstract"""
        soup = BeautifulSoup(open(self.file, encoding='utf-8'), "lxml")
        if self.outline == []:
            toc = soup.find_all(name='div', attrs={"class": "toc"})
            if len(toc) > 0:
                toc = toc[0].contents
                for t in toc:
                    self.outline.append((t.text.strip(), t.attrs['href'], t.attrs['class'][0]))
            else:
                return None

        self.parse_page(soup)

        if self.abstract == []:
            for id, (_, html, _) in enumerate(self.outline):
                soup = BeautifulSoup(open(os.path.join(self.path, html), encoding='utf-8'), "lxml")
                self.parse_page(soup)
                if self.abstract != []:
                    self.outline = self.outline[id + 1:]
                    self.has_metadata = True
                    break

    def get_content(self):
        """Extract journal and the body of a paper"""
        outline = []
        for bookmark, html, level in self.outline:
            soup = BeautifulSoup(open(os.path.join(self.path, html), encoding='utf-8'), "lxml")
            pgs = soup.find_all('p')
            end = True
            page = []
            for p in pgs:
                if 'style' in p.attrs:
                    if 'class' not in p.attrs or ('class' in p.attrs and 'reference' in bookmark.lower()):
                        text = p.text.strip()
                        if text == '':
                            continue
                        if end:
                            page.append(text)
                        else:
                            page[-1] += ' ' + text

                        if text[-1] not in ['.', ':', '!', '?', '。', '！', '？']:
                            end = False
                        else:
                            page[-1] = ' '.join(page[-1].replace('- ', '').split())
                            end = True

            if not end:
                page[-1] = ' '.join(page[-1].replace('- ', '').split())

            if level == 'toc0':
                self.content.append((bookmark, page))
                outline.append(bookmark)
            else:
                if bookmark == '':
                    if len(self.content) > 0:
                        self.content[-1][1].append(page)
                else:
                    try:
                        float(bookmark.split()[0].replace('.', ''))
                        self.content.append((bookmark, page))
                        outline.append(bookmark)
                    except:
                        if len(self.content) > 0:
                            self.content[-1][1].append(page)
                        else:
                            """ TODO: check for level2 """
                            pass

        self.has_content = True
        # update outline
        self.outline = outline



