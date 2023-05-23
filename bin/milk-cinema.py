import sys
import time
import threading
import webbrowser
import functools
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import argparse

def load_json(fname: str):
    with open(fname, 'r') as f:
        data = json.load(f)
    return data

def write_json(fname: str,data: dict):
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False, indent=4)

def start_server(ip,port,serve_path):
    server_address = (ip, port)
    Handler = functools.partial(SimpleHTTPRequestHandler, directory=serve_path)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()

def main():
    """Run cinema instance."""
    parser = argparse.ArgumentParser(
        description="Launch CINEMA viewing session.")
    parser.add_argument("-cinema_path", type=str, default=os.getenv('CINEMA_PATH'),
                        help="Installation path of Cinema:debye-scherrer.")
    parser.add_argument("-data_path", type=str, default=Path.cwd(),
                        help="Directory containing data.csv.")  
    parser.add_argument("-serve_path", type=str, default=Path.home(),
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
    args = parser.parse_args()

    args.cinema_path = Path(args.cinema_path)
    args.serve_path = Path(args.serve_path)
    args.data_path = Path(args.data_path)
    

    # Configure the http link
    html_path =  args.cinema_path / "main.html"
    assert html_path.is_file(), "Please specify a valid cinema path which contains main.html"
    url = f"http://{args.ip}:{args.port}/{html_path.relative_to(args.serve_path)}"

    #configure the database.json used by cinema
    csv_path = args.data_path / "data.csv"
    assert csv_path.is_file(), "Please specify a data_path with a data.csv file in the directory."
    databases_path = str(args.cinema_path / "databases.json")
    data = load_json(databases_path)
    data[args.databases_index]['name'] =  f"{args.databases_name}"
    data[args.databases_index]['directory'] =  f"{os.sep}{str(args.data_path.relative_to(args.serve_path))}"
    write_json(databases_path,data)

    # Launch server, open browser, and wait
    if args.run_server:
        threading.Thread(target=start_server,args=(args.ip,args.port,str(args.serve_path))).start()
        print(f"Serving: {url}")
        if args.open_browser:
            webbrowser.open_new(url)
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)

if __name__ == "__main__":
    main()
