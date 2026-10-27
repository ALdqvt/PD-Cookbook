import argparse
import sys
from pathlib import Path
import re
import logging
import biotite.sequence.io.fasta as fasta
import string

FASTA_EXTENSIONS = {".fa", ".fasta", ".faa"}
ID_RE = re.compile(r"\bid=(\d+)")
__version__ = "0.1.0"

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
        path = Path(args.input).expanduser().resolve()
        out_dir = (
            Path(args.output).expanduser().resolve()
            if args.output
            else path.parent / "split"
        )
        if not path.exists():
            logger.error(f"Input path not found: {path}")
            return 1

        if path.is_file():
            if path.suffix.lower() not in FASTA_EXTENSIONS:
                logger.error(f"Unsupported file extension: {path.suffix}")
                return 1
            files = [path]
        elif path.is_dir():
            files = sorted(
                p for p in path.iterdir() if p.suffix.lower() in FASTA_EXTENSIONS
            )
        else:
            logger.error(f"Unsupported input: {path}")
            return 1

        if not files:
            logger.warning(f"No fasta files found in {path}")

        for f in files:
            split_fasta_file(f, out_dir, args.plain)

        return 0

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return 1


def add_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and quit",
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input path, file or directory."
    )
    parser.add_argument("-o", "--output", help="Output path, a directory.")
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Keep original headers instead of Chai-1 format",
    )
    # parser.add_argument("-r", "--recursive", help="Operate recursively")
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-q", "--quiet", action="store_true", help="Show only errors"
    )
    verbosity_group.add_argument(
        "-V", "--verbose", action="store_true", help="Increase verbosity"
    )
    return parser


def chain_name(index: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA, ..."""
    name = ""
    index += 1
    while index > 0:
        index, rem = divmod(index - 1, 26)
        name = string.ascii_uppercase[rem] + name
    return name


def split_fasta_file(fasta_file: Path, out_dir: Path, plain: bool = False) -> int:

    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for i, (header, sequence) in enumerate(fasta.FastaFile.read_iter(fasta_file)):
        if i == 0:
            # TODO: Add flag to check if user wants to also output the original sequence entry.
            continue
        match = ID_RE.search(header)
        if not match:
            logger.warning(f"No id found in header, skipping: {header}")
            continue
        out = fasta.FastaFile()
        if plain:
            out[header] = sequence
        else:
            for j, chain_seq in enumerate(sequence.split(":")):
                out[f"protein|name={chain_name(j)}"] = chain_seq
        out_file = out_dir / f"{fasta_file.stem}_{match.group(1)}.fa"
        out.write(out_file)
        count += 1

    logger.info(f"{fasta_file.name}: wrote {count} files")
    return count


if __name__ == "__main__":
    sys.exit(main())
