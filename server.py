# server.py - Ninja Proxy Core
import http.server, socketserver, urllib.request, os, zipfile, json, threading, webbrowser, io, base64, hashlib, ssl, subprocess, sys, socket
from urllib.parse import parse_qs, urlparse
import requests

PROXY_PORT = 8080
WEB_PORT = 8000
ATMOSPHERE_VERSION = "1.7.1"
HEKATE_VERSION = "6.0.8"
PAYLOAD_BIN = "hekate_ctcaer.bin"
HEKATE_PAYLOAD_B64 = ""

class NinjaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy.pac'):
            self.serve_pac()
        elif self.path == '/payload':
            self.serve_payload()
        elif self.path.startswith('/install'):
            self.serve_install()
        else:
            self.serve_ui()

    def serve_ui(self):
        html = open("index.html", "rb").read()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html)

    def serve_payload(self):
        global HEKATE_PAYLOAD_B64
        if not HEKATE_PAYLOAD_B64:
            url = f"https://github.com/CTCaer/hekate/releases/download/v{HEKATE_VERSION}/hekate_ctcaer_{HEKATE_VERSION}.zip"
            data = urllib.request.urlopen(url).read()
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                HEKATE_PAYLOAD_B64 = base64.b64encode(z.read(PAYLOAD_BIN)).decode()
        self.send_response(200)
        self.send_header('Content-type', 'application/octet-stream')
        self.end_headers()
        self.wfile.write(base64.b64decode(HEKATE_PAYLOAD_B64))

    def serve_install(self):
        step = parse_qs(urlparse(self.path).query).get('step', [None])[0]
        if step == 'atmosphere':
            url = f"https://github.com/Atmosphere-NX/Atmosphere/releases/download/{ATMOSPHERE_VERSION}/atmosphere-{ATMOSPHERE_VERSION}-master.zip"
        elif step == 'sigpatches':
            r = requests.get("https://github.com/HamletDuFromage/signature-patches/releases/latest", allow_redirects=False)
            tag = r.headers['Location'].split('/')[-1]
            url = f"https://github.com/HamletDuFromage/signature-patches/releases/download/{tag}/sigpatches.zip"
        else:
            self.send_error(404); return
        data = urllib.request.urlopen(url).read()
        self.send_response(200)
        self.send_header('Content-type', 'application/zip')
        self.send_header('Content-Disposition', f'attachment; filename="{url.split("/")[-1]}"')
        self.end_headers()
        self.wfile.write(data)

    def serve_pac(self):
        pac = """
function FindProxyForURL(url, host) {
    if (shExpMatch(host, "*nintendo.*") || shExpMatch(host, "*akamai.*")) {
        return "PROXY 127.0.0.1:1";
    }
    return "DIRECT";
}
        """.strip()
        self.send_response(200)
        self.send_header('Content-type', 'application/x-ns-proxy-autoconfig')
        self.end_headers()
        self.wfile.write(pac.encode())

def start_dns_blocker():
    def handler(data, addr, sock):
        if b'nintendo' in data.lower():
            resp = b'\x00\x00\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00' + data[12:28] + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x00\x00\x04\x7f\x00\x00\x01'
            sock.sendto(resp, addr)
        else:
            fwd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            fwd.sendto(data, ('8.8.8.8', 53))
            sock.sendto(fwd.recv(1024), addr)
            fwd.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 53))
    print("[NINJA] DNS Blackhole Active")
    while True:
        data, addr = s.recvfrom(1024)
        threading.Thread(target=handler, args=(data, addr, s), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=start_dns_blocker, daemon=True).start()
    print(f"[NINJA PROXY] UI: http://localhost:{WEB_PORT}")
    print(f"[NINJA PROXY] PAC: http://localhost:{WEB_PORT}/proxy.pac")
    webbrowser.open(f"http://localhost:{WEB_PORT}")
    socketserver.TCPServer(("", WEB_PORT), NinjaHandler).serve_forever()
