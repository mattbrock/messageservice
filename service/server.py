from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader
import cgi

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/':
      self.path = '/index.html'
    try:
      env = Environment(loader=FileSystemLoader('.'))
      template = env.get_template(self.path[1:])
      with open('message.dat', 'r') as file:
        message = file.read().replace('\n', '')
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes(template.render(message=message), 'utf-8'))
    except:
      self.send_response(404)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(b'404 - Not Found')

  def do_POST(self):
    form = cgi.FieldStorage(
    fp=self.rfile,
    headers=self.headers,
    environ={'REQUEST_METHOD': 'POST',
             'CONTENT_TYPE': self.headers['Content-Type'],
            }
    )

    message = form.getvalue("message")

    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(b'Received new message: ' + message.encode())
    with open("message.dat", "w") as text_file:
      text_file.write("%s" % message)

httpd = HTTPServer(('', 8080), SimpleHTTPRequestHandler)
httpd.serve_forever()
