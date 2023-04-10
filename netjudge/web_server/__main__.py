"""Web server."""
from http.server import ThreadingHTTPServer

from netjudge.email_helper.mailer_configs import load_configs

from netjudge.web_server.MyHTTPRequestHandler import MyServer

super_secret_cookie = None


def main():
    """Main web server function."""
    configs = load_configs('mailer.cfg')

    httpd = ThreadingHTTPServer((configs['Web server']['hostname'], int(configs['Web server']['port'])), MyServer)
    print(f"Started server on http://{configs['Web server']['hostname']}:{configs['Web server']['port']}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    print(f"Stopped server")


if __name__ == '__main__':
    main()
