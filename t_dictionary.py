#! /usr/bin/env python2

from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import argparse


class SimpleMeanings:
    def __init__(self, word_type, meanings):
        self.word_type = word_type
        self.meanings = meanings


class Tense:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Word:
    def __init__(self, name):
        self.name = name
        self.pronunciations = []
        self.simple_meanings = []
        self.tenses = []


class TDictionary:
    def __init__(self):
        self.last_search_word = None

    def translate(self, keyword):
        self.last_search_word = self.query_and_parse(keyword)
        return self.last_search_word

    def query_and_parse(self, keyword):
        raise NotImplementedError("To be implemented by subclasses.")

    def simple_print(self, word=None):
        if not word:
            word = self.last_search_word
        if not word:
            print('Nothing found.')
            return

        print('Word:')
        print('\t' + word.name)

        print('Pronunciations:')
        for pronunciation in word.pronunciations:
            print('\t' + pronunciation)

        print('Simple Meanings:')
        for simple_meaning in word.simple_meanings:
            print('\t' + simple_meaning.word_type, end='\t')
            for meaning in simple_meaning.meanings:
                print(meaning, end='')
            print()

        print('Tenses:')
        for tense in word.tenses:
            print('\t' + tense.name, end='\t')
            print(tense.value)


class ICIBA(TDictionary):
    def __init__(self):
        TDictionary.__init__(self)
        self.base_url = 'https://www.iciba.com/'

    def query_and_parse(self, keyword):
        html = self.get_raw_html(keyword)
        if not html:
            return None

        html = html.replace('class=""', '')  # BeautifulSoup does not work well on this
        soup = BeautifulSoup(html, 'html.parser')

        # world
        word_name = soup.select_one('h1.keyword').text.strip()
        word = Word(word_name)

        # pronunciations
        pronunciation_tags = soup.select('div.base-speak > span > span')
        for pronunciation_tag in pronunciation_tags:
            word.pronunciations.append(pronunciation_tag.text.strip())

        # Simple Meanings
        simple_meaning_list_tags = soup.select('ul.base-list > li')
        for simple_meaning_list_tag in simple_meaning_list_tags:
            word_type = simple_meaning_list_tag.select_one('span.prop').text.strip()
            meanings = []
            for meaning_tag in simple_meaning_list_tag.select('p > span'):
                meanings.append(meaning_tag.text.strip())
            word.simple_meanings.append(SimpleMeanings(word_type, meanings))

        # Tenses
        tense_list_tags = soup.select('li.change > p > span')
        for tense_list_tag in tense_list_tags:
            tense_name = tense_list_tag.find(text=True, recursive=False).string.strip()
            tense_value = tense_list_tag.select_one('a').text.strip()
            word.tenses.append(Tense(tense_name, tense_value))

        return word

    def get_raw_html(self, keyword):
        r = requests.get(self.base_url + keyword, timeout=5, allow_redirects=False)
        if r.status_code != 200:
            return None
        return r.text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chinese -> English translations')
    parser.add_argument('word', help='The English word to be translated')
    args = parser.parse_args()
    i = ICIBA()
    i.translate(args.word)
    i.simple_print()
