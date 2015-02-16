#! /usr/bin/env python

import argparse
import codecs
import os
import unicodedata


def check_files(file_list):
    """Checks if all given files exist/are readable by the user"""
    for file_name in file_list:
        if not os.access(file_name, os.R_OK):
            return False
    return True


def strip_punctuation(text):
    """Remove any punctuation characters from the text"""
    punctuation_cats = set(['Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps'])
    return ''.join(x for x in text
                   if unicodedata.category(x) not in punctuation_cats)


def load_ignores(args):
    """Load ignore words list from given file (one word per line)"""
    if args.ignore and check_files([args.ignore]):
        with codecs.open(args.ignore, "r", "latin1") as f:
            return f.read().splitlines()
    else:
        return []


def count_words(args):
    """Count the number of times each word appears in the text file(s)"""

    counter = {}        # will contain dictionary of words and frequencies
    total = 0           # counts total number of words in input text(s)

    ignore_list = load_ignores(args)

    # process every input file given line by line and word by word
    for current_file in args.input_files:
        with codecs.open(current_file, "r", "latin1") as f:
            for line in f:
                for current_word in line.split():
                    current_word = strip_punctuation(current_word)
                    if args.case_insensitive:
                        current_word = current_word.lower()

                    total += 1

                    # skip over ignored words
                    if current_word in ignore_list:
                        continue

                    # increase word count each time we find the word
                    if current_word in counter:
                        counter[current_word] += 1
                    else:
                        counter[current_word] = 1

    # list of tuples containing the word and how many times it appeared
    freq = [(v, k) for (k, v) in counter.items()]

    # sort it and compute the relative frequency
    sorted_freq = [(k, v, float(k)/total) for k, v in sorted(freq, reverse=True)]
    uniques = len(sorted_freq)

    # return (up to) the number of words requested or all if not specified
    results = sorted_freq[:args.words] if args.words else sorted_freq
    return results, total, uniques


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Count the frequency of words")
    p.add_argument("-w", "--words", type=int,
                   help="Number of words to include in wordlist")
    p.add_argument("-i", "--ignore",
                   help="Name of file containing list of words to ignore")
    p.add_argument("input_files", nargs="+", help="Name of input file(s)")
    p.add_argument("-f", "--frequencies", action="store_true",
                   help="Display raw and relative frequencies with results")
    p.add_argument("-c", "--case-insensitive", action="store_true",
                   help="Count word frequencies case insensitively")
    p.add_argument("-t", "--totals", action="store_true",
                   help="Show total number of words and unique words in text")

    args = p.parse_args()

    if check_files(args.input_files):
        results, total, uniques = count_words(args)
        for line in results:
            if args.frequencies:
                try:
                    print u"{:21} {:8} {:18}".format(line[1], line[0], line[2])
                except:
                    # don't print the line if it cannot be displayed by terminal
                    pass
            else:
                try:
                    print line[1]
                except:
                    # don't print the line if it cannot be displayed by terminal
                    pass

        if args.totals:
            print "Total words:", total
            print "Total unique words:", uniques
