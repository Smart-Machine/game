from http.server import HTTPServer, BaseHTTPRequestHandler


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("It Works!", "utf-8"))

    def do_POST(self):
        print("Processing a POST request:")
        print(self.request)
        print(self.headers)
        content_length = int(self.headers.get("Content-Length"))
        if not content_length:
            print("There isn't a content_length")
            return
        body = self.rfile.read(content_length)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)


print("Listening on port :6969")
httpd = HTTPServer(("0.0.0.0", 6969), MyHandler)
httpd.serve_forever()
