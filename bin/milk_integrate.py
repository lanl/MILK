import sys
import argparse
from pathlib import Path
from multiprocessing import freeze_support
from MILK.integration.integrate import write_json, main

def get_arguments():
    """get_arguments parses command-line arguments.

    Returns:
        object: Parsed command-line argument.
    """
    if '-t' in sys.argv:
        print("Exporting json template.")
        write_json()
        exit()

    # Parse user arguments
    welcome = "Commandline multigeometry integration tool for tifs."

    # parse command line
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument("FILE", nargs="+",
                        help="Files to be integrated. Can contain wilds. Auto sorted. Same number of arguments as detectors.")
    parser.add_argument("-j", "--json", type=str, required=True,
                        help="json file containing integration details. Call code with only -t to generate template json.")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Directory where to store the output data. Default is data directory of first file.")
    parser.add_argument("-w", "--overwrite", action="store_true",
                        help="If false and data exists, do nothing.")
    parser.add_argument("-p", "--poolsize", type=int, default=None,
                        help="If set use python parallel map over files.")
    parser.add_argument("-f", "--format", type=str, nargs="+",
                        choices=["dat", "xy", "xye", "xy-noheader", "fxye", "esg", "esg1", "esg_detector"], default=[],
                        help="Output file format, dat is pyFAI default, xy, and xye are headerless where is e includes error,fyxe is gsas formatted xye, esg is MAUD format.")
    parser.add_argument("-hp", "--histogram_plot", action="store_true",
                        help="Export diffraction histogram plot.")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Turn off terminal messages and progress bar.")

    args = parser.parse_args()

    if args.output is not None:
        args.output = Path(args.output)

    return args

def entry_point():
    """Entry point for milk_integration commandline call."""
    freeze_support()
    args = get_arguments()
    main(files=args.FILE, 
         json_file=args.json, 
         output=args.output,
         overwrite=args.overwrite, 
         poolsize=args.poolsize, 
         formats=args.format, 
         histogram_plot=args.histogram_plot, 
         quiet=args.quiet)