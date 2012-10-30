# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import time
import strdata


def escape_if_necessary(what):
    what = str(what)
    if len(what) is 1:
        what = u"[%s]" % what

    return what


def get_stripped_lines(string, ignore_lines_starting_with=''):
    string = str(string)
    lines = [str(l.strip()) for l in string.splitlines()]
    if ignore_lines_starting_with:
        filter_func = lambda x: x and not x.startswith(
            ignore_lines_starting_with)
    else:
        filter_func = lambda x: x

    lines = filter(filter_func, lines)

    return lines


def split_wisely(string, sep, strip=False):
    string = str(string)
    if strip:
        string = string.strip()
    else:
        string = string.strip("\n")
    sep = str(sep)

    regex = re.compile(escape_if_necessary(sep),  re.str | re.M | re.I)

    items = filter(lambda x: x, regex.split(string))
    if strip:
        items = [i.strip() for i in items]
    else:
        items = [i.strip("\n") for i in items]

    return [str(i) for i in items]


def wise_startswith(string, seed):
    string = str(string).strip()
    seed = str(seed)
    regex = u"^%s" % re.escape(seed)
    return bool(re.search(regex, string, re.I))


def remove_it(string, what):
    return str(re.sub(str(what), "", str(string)).strip())


def column_width(string):
    l = 0
    for c in str(string):
        if strdata.east_asian_width(c) in "WF":
            l += 2
        else:
            l += 1
    return l


def rfill(string, times, char=u" ", append=u""):
    string = str(string)
    missing = times - column_width(string)
    for x in range(missing):
        string += char

    return str(string) + str(append)


def getlen(string):
    return column_width(str(string)) + 1


def dicts_to_string(dicts, order):
    escape = "#{%s}" % str(time.time())

    def enline(line):
        return str(line).replace("|", escape)

    def deline(line):
        return line.replace(escape, '\\|')

    keys_and_sizes = dict([(k, getlen(k)) for k in dicts[0].keys()])
    for key in keys_and_sizes:
        for data in dicts:
            current_size = keys_and_sizes[key]
            value = str(data.get(key, ''))
            size = getlen(value)
            if size > current_size:
                keys_and_sizes[key] = size

    names = []
    for key in order:
        size = keys_and_sizes[key]
        name = u" %s" % rfill(key, size)
        names.append(enline(name))

    table = [u"|%s|" % "|".join(names)]
    for data in dicts:
        names = []
        for key in order:
            value = data.get(key, '')
            size = keys_and_sizes[key]
            names.append(enline(u" %s" % rfill(value, size)))

        table.append(u"|%s|" % "|".join(names))

    return deline(u"\n".join(table) + u"\n")


def parse_hashes(lines):
    escape = "#{%s}" % str(time.time())

    def enline(line):
        return str(line.replace("\\|", escape)).strip()

    def deline(line):
        return line.replace(escape, '|')

    def discard_comments(lines):
        return [line for line in lines if not line.startswith('#')]

    lines = discard_comments(lines)
    lines = map(enline, lines)

    keys = []
    hashes = []
    if lines:
        first_line = lines.pop(0)
        keys = split_wisely(first_line, u"|", True)
        keys = map(deline, keys)

        for line in lines:
            values = split_wisely(line, u"|", True)
            values = map(deline, values)
            hashes.append(dict(zip(keys, values)))

    return keys, hashes


def parse_multiline(lines):
    multilines = []
    in_multiline = False
    for line in lines:
        if line == '"""':
            in_multiline = not in_multiline
        elif in_multiline:
            if line.startswith('"'):
                line = line[1:]
            if line.endswith('"'):
                line = line[:-1]
            multilines.append(line)
    return u'\n'.join(multilines)
