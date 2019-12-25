#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from typing import List

from bs4 import BeautifulSoup

from common import smart_comparing_names, get_norm_text
from base_parser import BaseParser


class IgromaniaRu_Parser(BaseParser):
    def get_site_name(self):
        import os.path
        return os.path.splitext(os.path.basename(__file__))[0]

    def _parse(self) -> List[str]:
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
        }
        form_data = {
            'mode': '11',
            's': '1',
            'p': '1',
            'fg': 'all',
            'fp': 'all',
            'fn': self.game_name
        }

        url = 'https://www.igromania.ru/-Engine-/AJAX/games.list.v2/index.php'
        rs = self.send_post(url, headers=headers, data=form_data)
        root = BeautifulSoup(rs.content, 'html.parser')

        for game_block in root.select('.gamebase_box'):
            title = get_norm_text(game_block.select_one('.release_name'))
            if not smart_comparing_names(title, self.game_name):
                continue

            genres = [get_norm_text(a) for a in game_block.select('.genre > a')]

            # Сойдет первый, совпадающий по имени, вариант
            return genres

        self.log_info(f'Not found game {self.game_name!r}')
        return []


def get_game_genres(game_name: str, *args, **kwargs) -> List[str]:
    return IgromaniaRu_Parser(*args, **kwargs).get_game_genres(game_name)


if __name__ == '__main__':
    from common import _common_test
    _common_test(get_game_genres)

    # Search 'Hellgate: London'...
    #     Genres: ['Боевик', 'Боевик от первого лица', 'Боевик от третьего лица', 'Ролевая игра']
    #
    # Search 'The Incredible Adventures of Van Helsing'...
    #     Genres: ['Ролевая игра', 'Боевик', 'Боевик от третьего лица']
    #
    # Search 'Dark Souls: Prepare to Die Edition'...
    #     Genres: []
    #
    # Search 'Twin Sector'...
    #     Genres: ['Боевик', 'Боевик от первого лица']
    #
    # Search 'Call of Cthulhu: Dark Corners of the Earth'...
    #     Genres: ['Боевик', 'Ужасы', 'Боевик от первого лица', 'Приключение']
