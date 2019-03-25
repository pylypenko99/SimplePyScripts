#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from glob import iglob, escape
import os


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)

        num /= 1024.0

    return "%3.1f %s" % (num, 'TB')


# FIXME: glob ignored dot folders and files
#        Examples: .git/ .idea/ .gitignore
def get_dir_total_size(dir_name: str) -> (int, str):
    total_size = 0

    for file_name in iglob(escape(dir_name) + '/**', recursive=True):
        try:
            if os.path.isfile(file_name):
                total_size += os.path.getsize(file_name)

        except Exception as e:
            print('File: "{}", error: "{}"'.format(file_name, e))

    return total_size, sizeof_fmt(total_size)


if __name__ == '__main__':
    paths = [r"C:\Users\Default", r"C:\Program Files (x86)", os.path.expanduser(r'~\Desktop')]

    for path in paths:
        size, size_str = get_dir_total_size(path)
        print(f'"{path}": {size} bytes / {size_str}')
