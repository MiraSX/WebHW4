from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from datetime import datetime
import mimetypes
import pathlib
import socket
from threading import Thread
import json


class MessageMeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        
        if url.path == "/":
            self._render("index.html")
        elif url.path == "/message":
            self._render("message.html")
        else:
            if pathlib.Path().joinpath(url.path[1:]).exists():
                self.send_static()
            else:
                self._render('error.html')
        

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        send_files(body)


    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def _render(self, filename, status_code=200):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        with open(filename, "rb") as fh:
            self.wfile.write(fh.read())

def run(server=HTTPServer, handler=MessageMeHandler):
    server_http = server(("127.0.0.1", 3000), handler)
    try:
        server_http.serve_forever()
    except KeyboardInterrupt:
        server_http.server_close()


def save_files(data):
    data = urllib.parse.unquote_plus(data.decode())
    cur_time = datetime.now()
    parsed_data = {str(cur_time): {k: v for k, v in [el.split("=") for el in data.split("&")]}} 
    with open('storage/data.json', 'a') as fn:
        json.dump(parsed_data, fn, indent=2)

def send_files(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, ("127.0.0.1", 5000))
    client_socket.close()

def run_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 5000))
    try:
        while True:
            data = server_socket.recv(1024)
            save_files(data)
    except KeyboardInterrupt:
        server_socket.close()



if __name__ == "__main__":
    thread_server = Thread(target=run)
    thread_server.start()

    thread_socket = Thread(target=run_socket_server())
    thread_socket.start()