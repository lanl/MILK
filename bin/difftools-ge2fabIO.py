from pathlib import Path
import fabio
import argparse
from multiprocessing import Pool, freeze_support
from functools import partial
import tqdm
import math
import os


def get_arguments():
    """Parse commandline arguments."""
    welcome = "Commandline conversion of 1ID edf.ge# detector files to fabIO compatible format."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument("FILE", nargs="+", type=str,
                        help="Input ge file(s) to convert. Wild cards can be used in file names.")
    parser.add_argument("-o", "--output", nargs="+", type=str, default=None,
                        help="Output directory. Default is input file directory.")
    parser.add_argument("-f", "--format", type=str,
                        choices=["EDF"], default="EDF", help=argparse.SUPPRESS)
    parser.add_argument("-p", "--pool-size", type=int, default=math.ceil(
        os.cpu_count()*0.8), help="Number of CPUs to use during conversion.")
    parser.add_argument("-d", "--delete", type=str2bool, default=False,
                        help="Overwrite files. If False files are not processed.")
    opts = parser.parse_args()
    return opts


def str2bool(v):
    """Convert string to bool."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('true'):
        return True
    elif v.lower() in ('false'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def process(opts, file):
    """Read edf.ge# files from 1ID and write out corresponding fabIO file."""
    # Get the header
    header = fabio.openimage.openheader(file)
    header = header.header

    # Parse header
    if header["DataType"] == 'UnsignedShort':
        nbyte = 2
        dtype = 'int16'
    else:
        raise TypeError(f"Unexpected type {header['DataType']} in header.")

    # Read in image data
    bi = fabio.binaryimage.BinaryImage()
    images = []
    for iframe in range(0, int(header["Num_Images"])):
        bi.read(file,
                int(header["Dim_1"]),
                int(header["Dim_2"]),
                int(header["EDF_HeaderSize"])+iframe*nbyte *
                int(header["Dim_1"])*int(header["Dim_2"]),
                dtype)
        images.append(bi.data)

    # Export using fabIO writer
    edf = fabio.edfimage.EdfImage(data=images[0], header=header)
    for image in images[1:]:
        edf.append_frame(data=image)
    if opts.format in "EDF":
        edf.write(output(file, opts.output))
    elif opts.format in "TIF":
        fname = output(file, opts.output)
        edf.convert("tif").save(fname.replace(".edf", ".tiff"))
    else:
        raise NotImplementedError(
            f"Format {opts.format} has not been added yet.")


def output(file, output):
    """Parse output file name assuming end of file is .edf.ge#"""
    if output is None:
        output = file.parent
    return Path(output) / Path(file).stem


def main():
    """Main routine."""
    opts = get_arguments()

    # Get files
    files = []
    for file in opts.file:
        tmp_files = sorted([str(p) for p in Path().rglob(file)])
        for tmp_file in tmp_files:
            files.append(tmp_file)

    if not opts.delete:
        # Clean file list
        for i, file in enumerate(reversed(files)):
            fullfile = Path(output(file, opts.output))
            if fullfile.is_file():
                files.pop(i)
                print(f"Skipping already processed file: {file}")

    if files != []:
        print("Processing files.")
        with Pool(opts.pool_size) as pool:
            list(tqdm.tqdm(pool.imap(partial(process, opts), files), total=len(files)))
    else:
        print("Nothing to be done.")


if __name__ == "__main__":
    freeze_support()
    main()
