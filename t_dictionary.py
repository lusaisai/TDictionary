#! /usr/bin/env python

from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import click


class SimpleMeanings:
    def __init__(self, word_type, meanings):
        self.word_type = word_type
        self.meanings = meanings


class CollinsMeaning:
    def __init__(self, word_type, chinese_description, english_description):
        self.word_type = word_type
        self.chinese_description = chinese_description
        self.english_description = english_description
        self.examples = []


class SingleCollinsExample:
    def __init__(self, english_sentence, chinese_sentence, highlight_word):
        self.english_sentence = english_sentence
        self.chinese_sentence = chinese_sentence
        self.highlight_word = highlight_word


class Tense:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Word:
    def __init__(self, name):
        self.name = name
        self.pronunciations = []
        self.simple_meanings = []
        self.collins_meanings = []
        self.tenses = []


class TDictionary:
    def __init__(self):
        self.last_search_word = None

    def lookup(self, keyword):
        self.last_search_word = self.query_and_parse(keyword)
        return self.last_search_word

    def query_and_parse(self, keyword):
        raise NotImplementedError("To be implemented by subclasses.")

    @staticmethod
    def coalesce(*items):
        for item in items:
            if item:
                return item

    def simple_print(self, collins_count):
        if not self.last_search_word:
            print('Nothing found.')
            return

        print('=' * 88)
        print('Simple Dictionary')
        print('=' * 88)
        print('Word:')
        print('\t' + self.last_search_word.name)

        print('Pronunciations:')
        for pronunciation in self.last_search_word.pronunciations:
            print('\t' + pronunciation)

        print('Simple Meanings:')
        for simple_meaning in self.last_search_word.simple_meanings:
            print('\t' + simple_meaning.word_type, end='\t')
            for meaning in simple_meaning.meanings:
                print(meaning, end='')
            print()

        print('Tenses:')
        for tense in self.last_search_word.tenses:
            print('\t' + tense.name, end='\t')
            print(tense.value)

        print()
        print('=' * 88)
        print('Collins Dictionary')
        print('=' * 88)
        for index, collins_meaning in enumerate(self.last_search_word.collins_meanings[:collins_count]):
            print(str(index+1) + '\t' + collins_meaning.word_type + '\t' + collins_meaning.chinese_description)
            print('\t' + collins_meaning.english_description)
            for example in collins_meaning.examples:
                print('\t\t' + example.english_sentence)
                print('\t\t' + example.chinese_sentence)
                print()


class ICIBA(TDictionary):
    def __init__(self):
        TDictionary.__init__(self)
        self.base_url = 'http://www.iciba.com/'

    def query_and_parse(self, keyword):
        html = self.get_raw_html(keyword)
        if not html:
            return None

        html = html.replace('class=""', '')  # BeautifulSoup does not work well on this
        soup = BeautifulSoup(html, 'html.parser')

        # world
        keyword_tag = soup.select_one('h1.keyword')
        if not keyword_tag:
            return None

        word_name = keyword_tag.text.strip()
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

        self.parse_collins(soup, word)

        return word

    @staticmethod
    def parse_collins(soup, word):
        collins_sections = soup.select('div.collins-section > div.no-order > div.prep-order')
        for collins_section in collins_sections:
            para = collins_section.select_one('p.size-chinese')
            if not para:
                break
            word_type = para.select_one('span.family-english').text.strip()
            chinese_desc = para.select_one('span.family-chinese').text.strip()
            english_desc = para.select_one('span.prep-en').text.strip()
            collins_meaning = CollinsMeaning(word_type, chinese_desc, english_desc)

            examples = collins_section.select('div.text-sentence')
            for example in examples:
                english_sentence = example.select_one('p.family-english').text.strip()
                chinese_sentence = example.select_one('p.family-chinese').text.strip()
                try:
                    highlight_word = example.select_one('p.family-english > span > b').text.strip()
                except AttributeError:
                    highlight_word = word.name
                collins_meaning.examples.append(
                    SingleCollinsExample(english_sentence, chinese_sentence, highlight_word))

            word.collins_meanings.append(collins_meaning)

    def get_raw_html(self, keyword):
        r = requests.get(self.base_url + keyword, timeout=5, allow_redirects=False)
        if r.status_code != 200:
            return None
        return r.text

    def simple_print(self, collins_count):
        TDictionary.simple_print(self, collins_count)
        print('\nFor more, please check on: ' +
              self.base_url + (self.coalesce(self.last_search_word, Word(''))).name)


if __name__ == '__main__':
    @click.command()
    @click.argument('word')
    @click.option('-c', '--collins-count', default=2, type=int, help='Number of Collins items to show.')
    @click.option('-a', '--all-collins-items', is_flag=True,
                  help='Show all the Collins dictionary items')
    def cli(word, collins_count, all_collins_items):
        i = ICIBA()
        i.lookup(word)
        if all_collins_items:
            count = 9999
        else:
            count = collins_count

        i.simple_print(count)

    cli()
