from pathlib import Path
import os
import argparse
from MILK.cinema import cinema


def main():
    """Run cinema instance."""
    parser = argparse.ArgumentParser(
        description="Launch CINEMA viewing session.")
    parser.add_argument("-cinema_path", type=str, default=os.getenv('CINEMA_PATH').strip("'"),
                        help="Installation path of Cinema:debye-scherrer.")
    parser.add_argument("-data_path", type=str, default=Path.cwd(),
                        help="Directory containing data.csv.")
    parser.add_argument("-serve_path", type=str, default=Path.cwd(),
                        help="Both cinema and data path must be a child of serve_path.")
    parser.add_argument("-port", type=int, default=8080,
                        help="Port number to serve on.")
    parser.add_argument("-ip", type=str, default="127.0.0.1",
                        help="IP to serve on.")
    parser.add_argument("-databases_index", type=int, default=0,
                        help="Specifies database index in databases.json that will have its directory overwritten.")
    parser.add_argument("-databases_name", type=str, default='MILK',
                        help="Name in CINEMA databases.json.")
    parser.add_argument("-run_server", type=bool, default=True,
                        help="Run server at end of script.")
    parser.add_argument("-open_browser", type=bool, default=True,
                        help="Open url in browser.")
    parser.add_argument("-local_cinema", type=bool, default=True,
                        help="Run cinema from data_path.")
    args = parser.parse_args()

    cinema.main(cinema_path=args.cinema_path,
                data_path=args.data_path,
                serve_path=args.serve_path,
                port=args.port,
                ip=args.ip,
                databases_index=args.databases_index,
                databases_name=args.databases_name,
                run_server=args.run_server,
                open_browser=args.open_browser,
                local_cinema=args.local_cinema
                )


if __name__ == "__main__":
    main()
