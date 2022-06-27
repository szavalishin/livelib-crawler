import os
import argparse
from typing import List

from src.pagewalker import FilePageWalker
from src.crawler import TourCrawler


def parse_cmd() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='URL or path to the file(s)')
    parser.add_argument('out', type=str, help='output file name')
    parser.add_argument('-c', '--curators', nargs='+',
                        default=['Meredith', 'T_Solovey', 'Wender', 'Aleni11', 'deranged', 'Mar_sianka', 'num',
                                 'devga', '3oate', 'Sotofa'], help='space-separated list of curators')
    return parser.parse_args()


def main(url: str, filename: str, curators: List[str] = []):
    if url.startswith('http'):
        raise NotImplementedError(f'Crawler supports only saved HTML files, got URL: "{url}"')
    elif os.path.exists(url):
        print(f'Parsing files in "{url}"')
        pagewalker = FilePageWalker(url)
    else:
        raise RuntimeError(f'Path or URL does not exist: {url}')

    crawler = TourCrawler(pagewalker, curators=curators, verbose=True)
    crawler.parse_to_file(filename)
    print('Saved to', filename)


if __name__ == '__main__':
    try:
        args = parse_cmd()
        main(args.url, args.out, args.curators)
    except Exception as e:
        print('Error:', e)
