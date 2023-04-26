import argparse
from src.parser.parse import BookParser


def argparsing():
    argus = argparse.ArgumentParser()
    argus.add_argument(
        "--input-jsonb",
        dest="input_jsonb",
        help="Input file of jsonb",
        required=True,
        type=str,
    )
    argus.add_argument(
        "--input-images",
        dest="input_images",
        help="Input folder with images",
        required=False,
        type=str,
    )
    argus.add_argument(
        "-o",
        "--output-folder",
        dest="out",
        help="Output folder path",
        required=True,
        type=str,
    )
    argus.add_argument("-d", "--dataset", help="Existing dataset", required=False)
    return argus.parse_args()


args = argparsing()
bp = BookParser(
    input_file=args.input_jsonb,
    output_folder=args.out,
    dataset=args.dataset,
    image_folder=args.input_images,
)
bp.run()
bp.zip()
