import os
import ssl
import subprocess

from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer


CERT_FILE = "/tmp/ftps.pem"


def generate_cert():
    subprocess.run(
        [
            "openssl", "req", "-x509", "-nodes", "-days", "3650",
            "-newkey", "rsa:2048",
            "-keyout", CERT_FILE,
            "-out", CERT_FILE,
            "-subj", "/CN=ftps-demo",
        ],
        check=True,
        capture_output=True,
    )
    print("Self-signed certificate generated.")


def main():
    generate_cert()

    ftp_user = os.environ.get("FTP_USER", "demo")
    ftp_pass = os.environ.get("FTP_PASS", "demo1234")
    ftp_port = int(os.environ.get("FTP_PORT", "21"))
    passive_start = int(os.environ.get("PASSIVE_PORT_START", "60000"))
    passive_end = int(os.environ.get("PASSIVE_PORT_END", "60010"))

    upload_dir = "/home/ftpuser"
    os.makedirs(upload_dir, exist_ok=True)

    authorizer = DummyAuthorizer()
    authorizer.add_user(ftp_user, ftp_pass, upload_dir, perm="elradfmwMT")

    handler = TLS_FTPHandler
    handler.authorizer = authorizer
    handler.certfile = CERT_FILE
    handler.tls_control_required = False  # explicit TLS: cliente hace AUTH TLS
    handler.passive_ports = range(passive_start, passive_end + 1)

    server = FTPServer(("0.0.0.0", ftp_port), handler)
    print(f"FTPS server listening on port {ftp_port} (passive {passive_start}-{passive_end})")
    server.serve_forever()


if __name__ == "__main__":
    main()
