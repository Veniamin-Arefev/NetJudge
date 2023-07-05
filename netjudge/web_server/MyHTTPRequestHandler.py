from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import unquote_plus

from netjudge.common.configs import load_configs
from netjudge.common.logger import get_logger
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
    my_logger = get_logger(__name__)
    configs = load_configs()

    def interpret_answer(self, answer):
        if (answer is None):
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(bytes(answer, "utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        self.my_logger.info('"{}" {} {}'.format(*args))

    def do_GET(self):
        answer = None

        is_admin = check_is_admin(self.headers.get('Cookie'), self.configs['Web server']['super secret cookie'])

        if self.path == '/':
            answer = get_index_page(is_admin)

        self.interpret_answer(answer)

    def do_POST(self):
        answer = None

        is_admin = check_is_admin(self.headers.get('Cookie'), self.configs['Web server']['super secret cookie'])

        if self.path == '/data' and is_admin:
            body = self.rfile.read(int(self.headers['Content-Length']))

            body_fields = {key: value for key, value in
                           map(lambda x: map(lambda y: y.replace('\xa0', ' ').strip(), x.split('=')),
                               unquote_plus(body.decode('utf-8')).split('&'))}

            answer = get_data_page(body_fields['username'], body_fields['homework_name'])

        self.interpret_answer(answer)
