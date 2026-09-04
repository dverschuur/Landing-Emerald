"""Servidor local de desarrollo con fallback de SPA.

El servidor estatico de Python devuelve 404 en /home, /about, etc. porque
esos archivos no existen: son rutas del router. Este script sirve el
archivo real cuando existe y, si no, entrega index.html para que el
App Shell resuelva la ruta. Es el mismo comportamiento que _redirects,
vercel.json o .htaccess en produccion.

    python serve.py            # http://127.0.0.1:8000
    python serve.py 3000       # otro puerto
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))


class SPARequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        disk_path = self.translate_path(self.path)
        if not (os.path.isfile(disk_path) or os.path.isdir(disk_path)):
            # Solo las rutas del router (sin extension) caen en index.html;
            # un .js o .png que falta debe seguir dando 404.
            last_segment = self.path.split('?')[0].rstrip('/').rsplit('/', 1)[-1]
            wants_html = 'text/html' in self.headers.get('Accept', '')
            if '.' not in last_segment or wants_html:
                self.path = '/index.html'
        return super().send_head()

    def end_headers(self):
        # En desarrollo conviene ver siempre la ultima version del archivo.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(('127.0.0.1', port), SPARequestHandler)
    print('Sirviendo %s en http://127.0.0.1:%d  (Ctrl+C para detener)' % (ROOT, port))
    server.serve_forever()


if __name__ == '__main__':
    main()
