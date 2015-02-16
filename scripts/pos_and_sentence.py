#!/usr/bin/env python
'''
    @author Olexander Yermakov(mannavard1611@gmail.com)
'''
from collections import Counter
from collections import OrderedDict
import nltk
from nltk.tokenize import RegexpTokenizer
import argparse
import itertools
import sys

default_chunk_size = 10

def get_args():
    '''
        Parse command line arguments.
    '''
    parser = argparse.ArgumentParser()

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

    parser.add_argument('--count-raw',
            dest='is_raw',
            action='store_true',
            help='''Count raw frequency instead relative.''')

    parser.add_argument('--sentence-statistics',
            dest='is_sent',
            action='store_true',
            help='''Compute and plot sentence statistics.''')

    parser.add_argument('--pos-statistics',
            dest='is_pos',
            action='store_true',
            help='''Compute and plot part-of-speech statistics.''')

    parser.add_argument('--sentence-compare',
            dest='is_sent_cmp',
            action='store_true',
            help='''Plot all files on one graph.''')

    parser.add_argument('--chunk-size',
            dest='chunk_size',
            type=int,
            help='''Chunk size in sentences.''',)

    parser.add_argument('--max',
            dest='is_max',
            action='store_true',
            help='''Plot max line.''')

    parser.add_argument('--min',
            dest='is_min',
            action='store_true',
            help='''Plot min line.''')

    return parser.parse_args()

def get_files(files, is_single):
    '''
        Get texts from files
    '''
    try:
        files = {filename : open(filename).read().decode('utf-8') for filename in files.split(',')}
    except IOError, e:
        raise e

    if is_single:
        files = {', '.join(files.keys()) : ' '.join(files.values())}

    return files

def get_sentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    return sent_detector.tokenize(text)

def count_sentence_stat(files, chunk_size):
    '''
        Count min, average and max length of sentences in files.
    '''
    if chunk_size:
        default_chunk_size = chunk_size

    sent_stat = {}
    tokenizer = RegexpTokenizer(r'\w+')
    for filename, text in zip(files.keys(), files.values()):
        sent = get_sentences(text)
        stat = []
        for group in [sent[x: x+default_chunk_size] for x in xrange(0, len(sent), default_chunk_size)]:
            words = get_words(group)
            counters = []
            for word in words:
                counters.append(Counter(word))

            word_count = [sum(c.values()) for c in counters]
            stat.append([sum(max(counters).values()),
                    sum(min(counters).values()),
                    float(sum(word_count)) / float(len(counters))])
        sent_stat[filename] = stat

    return sent_stat

def count_avg_sentence_stat(files):
    '''
        Count min, average and max length of sentences in files.
    '''
    sent_stat = {}
    tokenizer = RegexpTokenizer(r'\w+')
    for filename, text in zip(files.keys(), files.values()):
        sent = get_sentences(text)
        words = get_words(sent)

        counters = []
        for word in words:
            counters.append(Counter(word))

        word_count = [sum(c.values()) for c in counters]
        sent_stat[filename] = {'max' : sum(max(counters).values()),
                'min' : sum(min(counters).values()),
                'avg' : float(sum(word_count)) / float(len(counters))}

    return sent_stat

def get_words(text):
    tokenizer = RegexpTokenizer(r'\w+')
    return map((lambda s: tokenizer.tokenize(s)), text)

def count_pos_stat(files, is_raw):
    '''
        Count frequency of POS in text.
    '''
    pos_stat = {}
    for filename, text in zip(files.keys(), files.values()):
        words = get_words([text])[0]
        words = nltk.pos_tag(words)
        tags = map(lambda pair: pair[1], words)
        tags = Counter(tags)
        if is_raw:
            pos_stat[filename] = {k : v for k, v in zip(tags.keys(), tags.values())}
        else:
            pos_stat[filename] = {k : float(v)/sum(tags.values()) for k, v in zip(tags.keys(), tags.values())}

        pos_stat[filename] = OrderedDict(reversed(sorted(pos_stat[filename].items(), key=lambda x: x[1])))

    return pos_stat

def column(arr, i):
    return [row[i] for row in arr]

def plot_sent(sent_stat, avg_sent_stat, is_sent_cmp, is_max, is_min):
    '''
        Visualize sentece statistics results.
    '''

    for filename in sent_stat:
        maximum = column(sent_stat[filename], 0)
        minimum = column(sent_stat[filename], 1)
        avg = column(sent_stat[filename], 2)
        leg = []

        if not is_sent_cmp:
            plt.figure()

            plt.plot(avg)
            leg.append('Avg. num. of words in sentence (%.2f)' % (avg_sent_stat[filename]['avg']))

            if is_min:
                plt.plot(minimum)
                leg.append('Min num. of words in sentence (%.2f)' %(avg_sent_stat[filename]['min']))

            if is_max:
                plt.plot(maximum)
                leg.append('Max num. of words in sentence (%.2f)' %(avg_sent_stat[filename]['max']))
        else:
            plt.plot(column(sent_stat[filename], 2))

        if not is_sent_cmp:
            plt.title(filename)
            plt.legend(leg)
        else:
            plt.title(', '.join(sent_stat.keys()))
            plt.legend(sent_stat.keys())

        plt.ylabel('frequency')
        plt.xlabel('chunk')

    plt.show()

def plot_pos(pos_stat):
    '''
        Visualize part-of-speech statistics results.
    '''
    width = .35
    for filename, stat in zip(pos_stat.keys(), pos_stat.values()):
        fig = plt.figure()
        ax1 = plt.subplot(211)
        ind = np.arange(len(stat.values()))

        ax1.bar(ind + width, stat.values(), width)
        ax1.set_xticks(ind + width)
        ax1.set_xticklabels(['%s - %.2f' % (k, stat[k]) for k in stat])

        fig.autofmt_xdate(rotation='vertical', ha='center')
        plt.title(filename)

    plt.show()

def main():
    # get command line arguments.
    args = get_args()

    files = get_files(args.files, args.is_single)

    if args.is_sent:
        sent_stat = count_sentence_stat(files, args.chunk_size)
        avg_sent_stat = count_avg_sentence_stat(files)
        plot_sent(sent_stat, avg_sent_stat, args.is_sent_cmp, args.is_max, args.is_min)
    elif args.is_pos:
        pos_stat = count_pos_stat(files, args.is_raw)
        plot_pos(pos_stat)
    else:
        print 'Use --sentence-statistics or --pos-statistics flags'
        sys.exit()


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
