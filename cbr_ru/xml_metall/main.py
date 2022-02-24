#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import time

import db

from common import log
from parser import get_metal_rates, get_pair_dates


while True:
    log.info("Запуск")

    start_date = db.MetalRate.get_last_date()
    log.info(f"Поиск от {start_date}\n")

    for date_req1, date_req2 in get_pair_dates(start_date):
        log.info(f'Поиск за {date_req1} - {date_req2}')

        while True:
            try:
                rates = get_metal_rates(date_req1, date_req2)

                log.info(f'Найдено: {len(rates)}\n')
                if not rates:
                    log.info('Ничего не вернулось, похоже на ошибку сервиса. Нужно повторить')
                    time.sleep(60)
                    continue

                for metal_rate in rates:
                    db.MetalRate.add_from(metal_rate)

            except Exception:
                log.exception('Ошибка:')
                time.sleep(60 * 5)
                continue

            break

        time.sleep(60)

    log.info("Завершено.")

    time.sleep(60 * 8)
