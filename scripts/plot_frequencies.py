#!/usr/bin/env python
'''
    @author Olexander Yermakov(mannavard1611@gmail.com)
'''
from collections import Counter
import re
import argparse
import sys

# Size of chunk in words
default_block_size = 5000

def get_args():
    '''
        Parse command line arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--dictionary',
            dest='dictionary',
            type=str,
            help='Words dictionary',
            required=True)

    parser.add_argument('--files',
            dest='files',
            type=str,
            help='''List of files, that must be analized, seperated by commas.
                Example:
                    "file1.txt",
                    "file1.txt,file2.txt"''',
            required=True)

    parser.add_argument('--single-graph',
            dest='is_single',
            action='store_true',
            help='''Analyze all documents as one set and plot single graph if flag is used.''')

    parser.add_argument('--plot-individually',
            dest='is_individual',
            action='store_true',
            help='''Plot individual line for each word from dictionary.''')

    parser.add_argument('--chunk-size',
            dest='chunk_size',
            type=int,
            help='''Size of chunk in document.''')

    parser.add_argument('--count-raw',
            dest='is_raw',
            action='store_true',
            help='''Count raw frequency instead relative.''')

    return parser.parse_args()

def get_dict_words(dictionary):
    '''
        Get list of words, that must be analyzed.
    '''
    try:
        words = re.findall(r'\w+', open(dictionary).read().lower())
    except Exception, e:
        raise e

    return words

def get_analyze_words(input_str):
    '''
        Get texts for analyze.
    '''
    # --files option string. Split it to seperate filenames.
    file_list = input_str.split(',')

    try:
        # Make dictionary with list of words for each file.
        analyze_words = {filename : re.findall(r'\w+', open(filename).read().lower()) for filename in file_list}
    except Exception, e:
        raise e

    return analyze_words

def count_relative_freq(dict_words, analyze_words, is_single, is_individual, chunk_size):
    '''
        Count relative frequency.
    '''
    if chunk_size:
        block_size = chunk_size
    else:
        block_size = default_block_size

    freq = {}

    # If --single-graph is set, we analyze all files like one document.
    if is_single:
        analyze_words = {', '.join(analyze_words.keys()) : [item for sublist in analyze_words.values() for item in sublist]}

    for filename, words in analyze_words.items():
        unite_freq = []
            
        for group in [words[x:x+block_size] for x in xrange(0, len(words), block_size)]:
            if not is_individual:
                unite_freq.append([all_occurrences(dict_words, group) / float(block_size)])
            else:
                unite_freq.append([all_occurrences(dict_words, group, f) / float(block_size) for f in dict_words])


        freq[filename] = unite_freq

    return freq

def count_raw_freq(dict_words, analyze_words, is_single, is_individual, chunk_size):
    '''
        Count raw frequency.
    '''
    if chunk_size:
        block_size = chunk_size
    else:
        block_size = default_block_size

    freq = {}

    # If --single-graph is set, we analyze all files like one document.
    if is_single:
        analyze_words = {', '.join(analyze_words.keys()) : [item for sublist in analyze_words.values() for item in sublist]}

    for filename, words in analyze_words.items():
        unite_freq = []
            
        for group in [words[x:x+block_size] for x in xrange(0, len(words), block_size)]:
            if not is_individual:
                unite_freq.append([all_occurrences(dict_words, group)])
            else:
                unite_freq.append([all_occurrences(dict_words, group, f) for f in dict_words])


        freq[filename] = unite_freq

    return freq

def all_occurrences(needles, haystack, word=None):
    '''
        Count all occurrences from needles list in haystack list or just one word if word is not None.
    '''
    count = Counter(haystack)
    if word:
        return haystack.count(word)
    else:
        return sum([count[key] for key in needles])

def plot(freq):
    '''
        Plot bar chart using matplotlib.
    '''
    for filename in freq:
        plt.figure()
        plt.plot(freq[filename])
        plt.title(filename)
        plt.ylabel('frequency')
        plt.xlabel('block')
        
    plt.show()


def main():
    # get command line arguments.
    args = get_args()

    # Get dictionary whith results of counting.
    if args.is_raw:
        freq = count_raw_freq(get_dict_words(args.dictionary),
                get_analyze_words(args.files),
                args.is_single,
                args.is_individual,
                args.chunk_size)
    else:
        freq = count_relative_freq(get_dict_words(args.dictionary),
                get_analyze_words(args.files),
                args.is_single,
                args.is_individual,
                args.chunk_size)

    # Visualize results.
    plot(freq)


if __name__ == '__main__':
    # Check if plotting package is installed.
    try:
        import numpy as np
        from matplotlib import pyplot as plt
    except ImportError, e:
        print '''ERROR: Need to install python-numpy and python-matplotlib packages.
            Visit http://matplotlib.org/1.3.1/faq/installing_faq.html#installing-faq for instructions'''
        sys.exit()

    main()
