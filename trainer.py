#!/usr/bin/env python3
import argparse
import os
import string
import sys

import dotenv
import fasttext
from numpy.f2py.crackfortran import lenarraypattern
from spacy.lang.en.stop_words import STOP_WORDS

from lib import Config

config = dotenv.dotenv_values(".env")

def load_config(config, args):
    if args.epoch:
        print("Overriding epoch from command line")
        config["EPOCH"] = args.epoch
    if args.learning_rate:
        print("Overriding learning rate from command line")
        config["LEARNING_RATE"] = args.learning_rate
    if args.ngrams:
        print("Overriding ngrams from command line")
        config["NGRAMS"] = args.ngrams
    if args.ignore_case:
        print("Overriding ignore case from command line")
        config["IGNORE_CASE"] = args.ignore_case
    if args.ignore_punctuation:
        print("Overriding ignore punctuation from command line")
        config["IGNORE_PUNCTUATION"] = args.ignore_punctuation
    if args.ignore_stopwords:
        print("Overriding ignore stopwords from command line")
        config["IGNORE_STOPWORDS"] = args.ignore_stopwords
    if args.output:
        print("Overriding output file from the command line")
        config["MODEL"] = args.output
    return Config(config)

def main():
    global config
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input data for the model to train on")
    parser.add_argument("-o", "--output", help="Output file for the model")
    parser.add_argument("-e", "--epoch", help="Number of epochs to train the model", type=int)
    parser.add_argument("-l", "--learning-rate", help="Learning rate for the model", type=float)
    parser.add_argument("-n", "--ngrams", help="Number of word n-grams to use", type=int)
    parser.add_argument("--ignore-case", help="Ignore case when training the model", action="store_true")
    parser.add_argument("--ignore-punctuation", help="Ignore punctuation when training the model", action="store_true")
    parser.add_argument("--ignore-stopwords", help="Ignore stopwords when training the model", action="store_true")

    args = parser.parse_args()

    if not args.input:
        print("No input file specified.")
        sys.exit(1)
    output = args.output if args.output else config.get("MODEL")
    if not output:
        print("No output file specified.")
        sys.exit(1)
    config = load_config(config, args)

    epoch = config.epoch
    learning_rate = config.learning_rate
    ngrams = config.ngrams
    ignore_case = config.ignore_case
    ignore_punctuation = config.ignore_punctuation
    ignore_stopwords = config.ignore_stopwords
    print(args.input, epoch, learning_rate, ngrams, ignore_case, ignore_punctuation, ignore_stopwords)
    with open(args.input, "r") as file:
        lines = file.readlines()
    if not lines:
        print("No data in input file.")
        sys.exit(1)
    if ignore_case:
        lines = [line.lower() for line in lines]
    if ignore_punctuation:
        lines = [line.translate(str.maketrans('', '', string.punctuation)) for line in lines]
    if ignore_stopwords:
        lines = [" ".join([word for word in line.split() if word not in STOP_WORDS]) for line in lines]

    created_file = False
    if args.ignore_punctuation or args.ignore_case:
        with open("/tmp/training_data.txt", "w+") as out:
            for line in lines:
                out.write("__label__" + line)

        args.input = "/tmp/training_data.txt"
        created_file = True

    model = fasttext.train_supervised(input=args.input, epoch=epoch, lr=learning_rate, wordNgrams=ngrams)
    model.save_model(output)
    if created_file:
        os.remove(args.input)

def normalize_string(s):
    s = s.lower().strip()
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = " ".join([word for word in s.split() if word not in STOP_WORDS])
    return s

if __name__ == "__main__":
    main()