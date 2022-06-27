import os
import lxml.html as html

from glob import glob
from abc import ABC


class IPageWalker(ABC):
    def __init__(self, baseurl: str):
        pass

    def __next__(self):
        raise NotImplementedError
        return None

    def __iter__(self):
        return self


class FilePageWalker(IPageWalker):
    def __init__(self, baseurl: str):
        """
            :param baseurl: Path to the folder with html files
        """
        if len(baseurl) and '*' not in baseurl and not baseurl.endswith('html'):
            baseurl = os.path.join(baseurl, '*.html')
        self._pages = glob(baseurl)
        self._page = 0

    def __next__(self) -> html.HtmlElement:
        if self._page < len(self._pages):
            page = html.parse(self._pages[self._page]).getroot()
            self._page += 1
            return page

        raise StopIteration
