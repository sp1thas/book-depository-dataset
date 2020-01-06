# Parser

This submodule is about parsing and manipulating the raw data in order to create the dataset in a tabular format (`csv`).

## Usage

Use the parser directly from command line, just provide the `.jsonlines` file with raw data and the output directory.

```bash
python parse_dataset.py -h
optional arguments:
  -h, --help            show this help message and exit
  -i INP, --input-file INP
                        Input file path
  -o OUT, --output-folder OUT
                        Output folder path
```

### Working example
```bash
python parse_dataset.py -i /path/to/comments.jsonlines -o ../export
```

This script will create a collection of `.csv` files in `../export` folder.