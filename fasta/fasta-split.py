import argparse
import os
import sys
from pathlib import Path
import re
import glob
import logging
import biotite

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Fasta file splitter")
    parser = add_args(parser)
    args = parser.parse_args()

    if args.verbose:
        verbosity = logging.DEBUG
    elif args.quiet:
        verbosity = logging.ERROR
    else:
        verbosity = logging.INFO

    logging.basicConfig(
        level=verbosity,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        logger.info(__file__)
        # TODO:
        return 0
    except Exception as e:
        logger.error(f"An unexpected error ocured: {e}")
        return 1


def add_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-v", "--version", help="Show program version and quit")
    parser.add_argument("-i", "--input", help="Input path, file or directory.")
    parser.add_argument("-o", "--output", help="Output path, a directory.")
    parser.add_argument("-c", "--chai", help="Format output for chai-1")
    # parser.add_argument("-r", "--recursive", help="Operate recursively")
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-q", "--quiet", action="store_true", help="Show only errors"
    )
    verbosity_group.add_argument(
        "-V", "--verbose", action="store_true", help="Increase verbosity"
    )
    return parser


if __name__ == "__main__":
    sys.exit(main())
