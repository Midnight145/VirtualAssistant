#!/usr/bin/env python3

import string
import argparse
import sys
import fasttext

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input data for the model to train on")
    parser.add_argument("-o", "--output", help="Output file for the model")
    parser.add_argument("-e", "--epoch", help="Number of epochs to train the model", default=25, type=int)
    parser.add_argument("-l", "--learning-rate", help="Learning rate for the model", default=0.5, type=int)
    parser.add_argument("-n", "--ngrams", help="Number of word n-grams to use", default=2, type=int)
    parser.add_argument("--ignore-case", help="Ignore case when training the model", action="store_true", default=False)
    parser.add_argument("--ignore-punctuation", help="Ignore punctuation when training the model", action="store_true", default=False)

    args = parser.parse_args()

    if not args.input:
        print("No input file specified.")
        sys.exit(1)
    if not args.output:
        print("No output file specified.")
        sys.exit(1)

    with open(args.input, "r") as file:
        lines = file.readlines()
    if not lines:
        print("No data in input file.")
        sys.exit(1)
    if args.ignore_case:
        lines = [line.lower() for line in lines]
    if args.ignore_punctuation:
        lines = [line.translate(str.maketrans('', '', string.punctuation)) for line in lines]

    if args.ignore_punctuation or args.ignore_case:
        with open("/tmp/training_data.txt", "w+") as out:
            for line in lines:
                out.write("__label__" + line)

        args.input = "/tmp/training_data.txt"

    model = fasttext.train_supervised(input=args.input, epoch=args.epoch, lr=args.learning_rate, wordNgrams=args.ngrams)
    model.save_model(args.output)

    print(model.predict("What's the weather like today?"))
    print(model.predict("Set a timer for 5 minutes"))
    print(model.predict("Raise the volume"))
    print(model.predict("Play the music"))
    print(model.predict("Set a reminder for tomorrow at 5:30"))
    print(model.predict("Is it going to rain?"))
    print(model.predict("Tell me about world news"))

def normalize_string(s):
    s = s.lower().strip()
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s

if __name__ == "__main__":
    main()