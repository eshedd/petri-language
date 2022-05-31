import sys
import http.server
import socketserver

PORT = 8080

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    ".js": "application/javascript",
})

httpd = socketserver.TCPServer(("", PORT), Handler)
httpd.serve_forever()
