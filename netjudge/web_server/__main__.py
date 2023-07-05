"""Web server."""
from http.server import ThreadingHTTPServer

from netjudge.common.configs import load_configs
from netjudge.web_server.MyHTTPRequestHandler import MyServer
from netjudge.common.logger import get_logger

super_secret_cookie = None


def main():
    """Main web server function."""
    configs = load_configs()

    my_logger = get_logger(__name__)

    httpd = ThreadingHTTPServer((configs['Web server']['hostname'], int(configs['Web server']['port'])), MyServer)
    hostname = configs['Web server']['hostname'] if configs['Web server']['hostname'] != '0.0.0.0' else 'localhost'
    my_logger.info(f"Started server on http://{hostname}:{configs['Web server']['port']}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    my_logger.info(f"Stopped server")
