import pandas as pd
import argparse
import csv


def argparsing():
    argobj = argparse.ArgumentParser()
    argobj.add_argument('--input-folder', '-i', help="Input folder", type=str)
    argobj.add_argument('--output-folder', '-o', help='Output folder', type=str)
    return argobj.parse_args()


class Cleaner:

    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
