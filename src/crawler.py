import re
import pandas as pd
import lxml.html as html

from abc import ABC
from typing import List, Optional, Dict, Any

from pagewalker import IPageWalker


class ICrawler(ABC):
    def __init__(self, pagewalker: IPageWalker):
        self._walker = pagewalker

    def parse(self) -> Optional[pd.DataFrame]:
        for page in self._walker:
            pass  # Do smth
        return None

    def parse_to_file(self, filename: str) -> None:
        df = self.parse()
        df.to_excel(filename)


class TourCrawler(ICrawler):
    __bookrequest_link = 'https://www.livelib.ru/game/bookquest/entry/'
    __xlsx_hyperlink = '=HYPERLINK("{link}{app_id}", "заявка")'

    _columns = {'player_name': 'Игрок', 'app_id': 'Заявка', 'is_kamikaze': 'Камикадзе', 'curator': 'Куратор',
                'link': 'Ссылка', 'comment': 'Комментарий'}
    _sort_by = 'app_id'

    def __init__(self, pagewalker: IPageWalker, curators: List[str] = [], ignore_duplicates=True,
                 verbose=False):
        super().__init__(pagewalker=pagewalker)
        self._curators = list(curators)
        self._curators_lower = [x.lower() for x in curators]
        self._verbose = verbose
        self._ignore_duplicates = ignore_duplicates

    @property
    def curators(self) -> List[str]:
        return self._curators

    @curators.setter
    def curators(self, lst: List[str]):
        self._curators = lst
        self._curators_lower = [x.lower() for x in lst]

    def _process_entry(self, entry: Any) -> Dict[str, Any]:
        cols = {}

        cols['app_id'] = entry.attrib.get('id')[11:]
        cols['player_name'] = entry.find_class('a-login-black').pop(0).attrib.get('title')
        cols['desc'] = entry.find_class('description')[0].text_content().lower()
        cols['is_kamikaze'] = 'Да' if r'камикадзе' in cols['desc'] else 'Нет'
        curator = None
        comment = ''

        for c in self._curators_lower:
            if c in cols['desc']:
                if curator is None:
                    curator = c
                else:
                    comment += f'Warning: more than one curator is mentioned: "{c}"\n'

        cols['curator'] = curator
        cols['link'] = self.__xlsx_hyperlink.format(link=self.__bookrequest_link, app_id=cols['app_id'])
        cols['comment'] = comment

        return cols

    def parse_page(self, page: html.HtmlElement, df: pd.DataFrame = None) -> pd.DataFrame:
        if df is None:
            df = pd.DataFrame(columns=self._columns.values())

        for entry in page.get_element_by_id('entries'):
            cols = self._process_entry(entry)
            df.loc[len(df) + 1] = [cols[k] for k in self._columns.keys()]

        return df

    def parse(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=self._columns.values())

        for i, page in enumerate(self._walker):
            if self._verbose:
                print('Processing page', i + 1)
            df = self.parse_page(page, df)

        return df.sort_values(self._columns[self._sort_by], axis=0)


class TourCrawler2023(TourCrawler):
    _columns = {'player_name': 'Игрок', 'app_id': 'Заявка', 'is_kamikaze': 'Камикадзе', 'sweater': 'Свитер',
                 'curator': 'Куратор', 'link': 'Ссылка', 'comment': 'Комментарий'}

    __sweaters = {
        'плюшевый пингвин': re.compile(r'.*(плюшев\w+)|(пингвин\w+).*', re.IGNORECASE),
        'бутерброд с колбасой': re.compile(r'.*(бутерброд\w)|(колбас\w+).*', re.IGNORECASE),
        'радуга с блестками': re.compile(r'.*(радуг\w+)|(блестками).*', re.IGNORECASE),
    }

    @staticmethod
    def _add_comment(cols: Dict[str, Any], comment: str):
        cmt = cols['comment']
        cols['comment'] = comment if not isinstance(cmt, str) else '\n'.join((cmt, comment))

    def _process_entry(self, entry: Any) -> Dict[str, Any]:
        cols = super()._process_entry(entry)

        sweater = ''
        for name, rexp in self.__sweaters.items():
            if len(rexp.findall(cols['desc'])):
                if sweater != '':
                    sweater = '?'
                    self._add_comment(cols, 'Error: multiple sweater entries')
                    break
                sweater = name

        if sweater == '':
            self._add_comment(cols, 'Error: no sweater was recognized')

        cols['sweater'] = sweater

        return cols
