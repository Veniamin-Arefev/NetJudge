"""Web server."""
from http.server import HTTPServer

from netjudge.email_helper.mailer_configs import load_configs

from netjudge.web_server.MyHTTPRequestHandler import MyServer

super_secret_cookie = None


def main():
    """Main web server function."""
    configs = load_configs('mailer_ya.cfg')

    httpd = HTTPServer((configs['Web_server']['hostname'], int(configs['Web_server']['port'])), MyServer)
    print(f"Started server on http://{configs['Web_server']['hostname']}:{configs['Web_server']['port']}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    print(f"Stopped server")


if __name__ == '__main__':
    main()
