import argparse
import configparser
import re
from itertools import chain

p = argparse.ArgumentParser(description='Parses transform regex with substituted patterns.')
p.add_argument('file', help='A Splunk config file like transforms.conf.')
p.add_argument('stanza', help='The transform section/stanza.')
args = p.parse_args()

config = configparser.ConfigParser()

with open(args.file) as f:
    try:
        config.read_file(f)
    except configparser.MissingSectionHeaderError:
        f = chain(['[DEFAULT]'], f)
        config.read_file(f)


splunk_re_subst = re.compile(r'\[\[(?P<section>[^]]+?)(?::(?P<name>.+?))?\]\]')


def get_regex(section_name):
    # print('getting regex')
    regex = config.get(section_name, 'REGEX')
    matches = splunk_re_subst.findall(regex)
    if matches:
        # print(matches)
        for match in matches:
            # print(match)
            s, n = match
            # print(s, n)
            match_regex = get_regex(s)
            if n:
                regex = regex.replace(
                    '[[%s:%s]]' % (s, n),
                    '(?<%s>%s)' % (n, match_regex))
            else:
                regex = regex.replace(
                    '[[%s]]' % s,
                    '(%s)' % match_regex)
    return regex


def escape_delimiters(regex):
    return regex.replace('/', '\/')


def remove_empty_name_placeholders(regex):
    return regex.replace('?<>', '')


regex = get_regex(args.stanza)
regex = escape_delimiters(regex)
regex = remove_empty_name_placeholders(regex)
print(regex)
