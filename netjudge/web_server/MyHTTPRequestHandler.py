from http.server import BaseHTTPRequestHandler
from urllib.parse import unquote_plus

from netjudge.email_helper.mailer_configs import load_configs
from netjudge.web_server.page_generator import get_index_page, get_data_page


def check_is_admin(cookies_str: str, super_secret_cookie: str):
    if cookies_str:
        cookies = {key: value for key, value in
                   map(lambda x: map(lambda y: y.strip(), x.split('=', 1)), cookies_str.split(';'))
                   }

        return 'super_secret_cookie' in cookies.keys() and cookies['super_secret_cookie'] == super_secret_cookie

    return False


class MyServer(BaseHTTPRequestHandler):
    super_secret_cookie = None

    def do_GET(self):
        answer = None
        configs = load_configs('mailer.cfg')

        is_admin = check_is_admin(self.headers.get('Cookie'), configs['Web server']['super secret cookie'])

        if self.path == '/':
            answer = get_index_page(is_admin)

        if (answer is None):
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(bytes(answer, "utf-8"))

    def do_POST(self):
        answer = None
        configs = load_configs('mailer.cfg')

        is_admin = check_is_admin(self.headers.get('Cookie'), configs['Web server']['super secret cookie'])

        if self.path == '/data' and is_admin:
            body = self.rfile.read(int(self.headers['Content-Length']))

            body_fields = {key: value for key, value in
                           map(lambda x: map(lambda y: y.replace('\xa0', ' ').strip(), x.split('=')),
                               unquote_plus(body.decode('utf-8')).split('&'))}

            answer = get_data_page(body_fields['username'], body_fields['homework_name'])

        if (answer is None):
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(bytes(answer, "utf-8"))
