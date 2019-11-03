import socketserver
import logging
from http.server import BaseHTTPRequestHandler
import os


HOST = "0.0.0.0"
PORT = 8080


logger = logging.getLogger('HashSwarm-HealthCheck')


class HashSwarmHealthCheck(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        # Check the status of the hashswarm deamon
        status = os.system('systemctl is-active --quiet hashswarm')
        if status == 0:
            return {'status': 200, 'message': 'HashSwarm service is running'}
        else:
            return {'status': 500, 'message': 'HashSwarm service is not running'}

    def handle_http(self, status_code, message, path):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        return bytes(message, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['status'], opts['message'], self.path)
        self.wfile.write(response)


def main():
    with socketserver.TCPServer((HOST, PORT), HashSwarmHealthCheck) as httpd:
        logger.info(f"Starting healthcheck server on {HOST}:{PORT}...")
        httpd.serve_forever()


if __name__ == "__main__":
    # execute only if run as a script
    main()
