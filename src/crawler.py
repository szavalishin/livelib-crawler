import pandas as pd
import lxml.html as html

from abc import ABC
from typing import List

from pagewalker import IPageWalker


class ICrawler(ABC):
    def __init__(self, pagewalker: IPageWalker):
        self._walker = pagewalker

    def parse(self) -> pd.DataFrame:
        for page in self._walker:
            pass  # Do smth
        return None

    def parse_to_file(self, filename: str) -> None:
        df = self.parse()
        df.to_excel(filename)


class TourCrawler(ICrawler):
    __bookrequest_link = 'https://www.livelib.ru/game/bookquest/entry/'
    __columns = ['Заявка', 'Игрок', 'Камикадзе', 'Куратор', 'Ссылка', 'Комментарий']
    __sort_by = 'Заявка'
    __xlsx_hyperlink = '=HYPERLINK("{link}{app_id}", "заявка")'

    def __init__(self, pagewalker: IPageWalker, curators: List[str] = [], ignore_duplicates=True,
                 verbose=False):
        super().__init__(pagewalker=pagewalker)
        self._curators = curators
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

    def parse_page(self, page: html.HtmlElement, df: pd.DataFrame = None) -> pd.DataFrame:
        if df is None:
            df = pd.DataFrame(columns=self.__columns)

        for entry in page.get_element_by_id('entries'):
            app_id = entry.attrib.get('id')[11:]
            player_name = entry.find_class('a-login-black').pop(0).attrib.get('title')
            desc = entry.find_class('description').pop().text_content().lower()
            is_kamikaze = 'Да' if r'камикадзе' in desc else None
            curator = None
            comment = ''

            for c in self._curators_lower:
                if c in desc:
                    if curator is None:
                        curator = c
                    else:
                        comment += f'Warning: more than one curator is mentioned: "{c}"\n'

            link = self.__xlsx_hyperlink.format(link=self.__bookrequest_link, app_id=app_id)
            df.loc[len(df) + 1] = [app_id, player_name, is_kamikaze, curator, link, comment]

        return df

    def parse(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=self.__columns)

        for i, page in enumerate(self._walker):
            if self._verbose:
                print('Processing page', i + 1)
            df = self.parse_page(page, df)

        return df.sort_values(self.__sort_by, axis=0)
