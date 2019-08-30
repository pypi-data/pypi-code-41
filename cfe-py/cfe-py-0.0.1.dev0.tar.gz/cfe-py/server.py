#!/usr/bin/env python3
"""
Very simple HTTP server in python to list and update files.

Usage:
    ./cfe-server.py
    CFE_DIR=path/to/files PORT=8888 ./cfe-server.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json

def include_file(root,file_name):
    return not file_name[0] == "." and not "/." in file_name  and not "/." in root 

def list_files():
    path = os.getenv("CFE_DIR",".")
    file_list = []
    for root, directories, files in os.walk(path):
        for file_name in files:
            if include_file(root,file_name):
                file_list.append(os.path.join(root, file_name).replace(path,''))
    return file_list

def read_file(file_path):
    path = os.getenv("CFE_DIR",".")
    with open(f"{path}{file_path}","r") as f:
        content=f.read()
    return content
    
def write_file(file_path,content):
    path = os.getenv("CFE_DIR",".")
    with open(f"{path}{file_path}","wb") as f:
        f.write(content)

class CFEServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if "/files" == self.path:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', self.headers.get("Origin"))
            self.end_headers()
            self.wfile.write(json.dumps({"files":list_files()}).encode())
            return
        elif "?file=" in self.path:
            file_path = self.path.split("file=")[1]
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', self.headers.get("Origin"))
            self.end_headers()
            self.wfile.write(read_file(file_path.replace("%2F","/")).encode())
            return
        else:
            file_path = self.path
            if self.path in ["/",""]:
                file_path = "index.html"
            file_path = os.path.dirname(__file__)+"/public/"+file_path
            
            if not os.path.isfile(file_path):
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            content_type = "text/plain"
            if ".js" in file_path:
                content_type="application/javascript"
            if ".css" in file_path:
                content_type="text/css"
            if ".html" in file_path:
                content_type="text/html"

            self.send_header('Content-Type', content_type+"; charset=utf-8")
            self.send_header('Access-Control-Allow-Origin', self.headers.get("Origin"))
            self.end_headers()

            with open(f"{file_path}","r") as f:
                content=f.read()

            self.wfile.write(content.encode())
            return

    def do_POST(self):
        file_path = self.path.split("file=")[1].replace("%2F","/")
        content_length = int(self.headers['Content-Length']) 
        content = self.rfile.read(content_length)
        write_file(file_path,content)
        self.send_response(200)
        self.end_headers()
        
def run():
    port = int(os.getenv("PORT","8181"))
    address = os.getenv("ADDRESS","127.0.0.1")
    directory = os.getenv("CFE_DIR",".")

    server_address = (address, port)
    httpd = HTTPServer(server_address, CFEServer)
    print(f"Starting server on port {port} serving files from {directory}")

    httpd.serve_forever()

if __name__ == "__main__":
    run()
