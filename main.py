import os
import argparse
from typing import List

from src.pagewalker import FilePageWalker, IPageWalker
from src.crawler import TourCrawler, TourCrawler2023, ICrawler


def parse_cmd() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='URL or path to the file(s)')
    parser.add_argument('out', type=str, help='output file name')
    parser.add_argument('-c', '--curators', nargs='+',
                        default=['Meredith', 'T_Solovey', 'Wender', 'Aleni11', 'deranged', 'Mar_sianka', 'num',
                                 'devga', '3oate', 'Sotofa'], help='space-separated list of curators')
    parser.add_argument('-t', '--tour', default='2022', choices=['2022', '2023'])
    return parser.parse_args()


def get_walker(url: str) -> IPageWalker:
    if url.startswith('http'):
        raise NotImplementedError(f'Crawler supports only saved HTML files, got URL: "{url}"')
    elif os.path.exists(url):
        print(f'Parsing files in "{url}"')
        pagewalker = FilePageWalker(url)
    else:
        raise RuntimeError(f'Path or URL does not exist: {url}')

    return pagewalker


def get_crawler(tour: str, pagewalker: IPageWalker, curators: List[str]) -> ICrawler:
    crawler = {
        '2022': TourCrawler,
        '2023': TourCrawler2023,
    }.get(tour)

    if crawler is None:
        raise ValueError(f'Unknown tour "{tour}"')

    return crawler(pagewalker, curators=curators, verbose=True)


def main(url: str, filename: str, tour: str = '2022', curators: List[str] = []) -> None:
    pagewalker = get_walker(url)
    crawler = get_crawler(tour, pagewalker, curators)
    crawler.parse_to_file(filename)
    print('Saved to', filename)


if __name__ == '__main__':
    try:
        args = parse_cmd()
        main(args.url, args.out, args.tour, args.curators)
    except Exception as e:
        print('Error:', e)
