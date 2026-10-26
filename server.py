"""Serveur de la régie son : sert cue-player.html, cues.json et les fichiers audio (avec requêtes Range,
nécessaires pour se déplacer dans un morceau).

  python3 server.py [--port 8080] [--audio sons] [--bind 127.0.0.1]

Réglages possibles par variables d'environnement : CUE_PORT, CUE_AUDIO, CUE_BIND, CUE_BANNER (texte d'un
bandeau rouge, pour distinguer un environnement de test de la production).
"""
import argparse
import http.server
import mimetypes
import os
import sys
import urllib.parse

ICI = os.path.dirname(os.path.abspath(__file__))


def creer_handler(dossier_audio, banniere):
    class CueHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=ICI, **kwargs)

        def do_GET(self):
            chemin = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
            if chemin in ("", "/"):
                return self.envoyer_page()
            if chemin == "/cues.json":
                self.path = "/cues.json"
                return super().do_GET()
            if chemin.startswith("/audio/"):
                return self.envoyer_audio(chemin[len("/audio/"):])
            self.send_error(404)

        def envoyer_page(self):
            with open(os.path.join(ICI, "cue-player.html"), "rb") as f:
                corps = f.read()
            if banniere:
                bandeau = ('<div style="position:fixed;top:0;left:0;right:0;z-index:999;background:#b00020;color:#fff;'
                           'text-align:center;font:600 12px sans-serif;padding:2px">%s</div>' % banniere).encode()
                corps = corps.replace(b"<body>", b"<body>" + bandeau, 1)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

        def envoyer_audio(self, nom):
            racine = os.path.abspath(dossier_audio)
            fichier = os.path.abspath(os.path.join(racine, nom))
            if not fichier.startswith(racine + os.sep):
                return self.send_error(403, "Interdit")
            if not os.path.isfile(fichier):
                return self.send_error(404, "Fichier introuvable")
            taille = os.path.getsize(fichier)
            type_ = mimetypes.guess_type(fichier)[0] or "application/octet-stream"
            plage = self.headers.get("Range")
            debut, fin = 0, taille - 1
            if plage and plage.startswith("bytes="):
                d, _, f = plage[6:].partition("-")
                try:
                    if d == "":  # "bytes=-N" : les N derniers octets
                        debut = max(0, taille - int(f))
                    else:
                        debut = int(d)
                        fin = min(int(f), taille - 1) if f else taille - 1
                except ValueError:
                    return self.send_error(400, "Range invalide")
                if debut > fin or debut >= taille:
                    self.send_response(416)
                    self.send_header("Content-Range", "bytes */%d" % taille)
                    self.end_headers()
                    return
                self.send_response(206)
                self.send_header("Content-Range", "bytes %d-%d/%d" % (debut, fin, taille))
            else:
                self.send_response(200)
            self.send_header("Content-Type", type_)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(fin - debut + 1))
            self.end_headers()
            with open(fichier, "rb") as f:
                f.seek(debut)
                restant = fin - debut + 1
                while restant > 0:
                    bloc = f.read(min(1 << 20, restant))
                    if not bloc:
                        break
                    self.wfile.write(bloc)
                    restant -= len(bloc)

        def end_headers(self):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            super().end_headers()

        def log_message(self, format, *args):
            print("[serveur]", format % args)

    return CueHandler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=int(os.environ.get("CUE_PORT", 8080)))
    ap.add_argument("--audio", default=os.environ.get("CUE_AUDIO", os.path.join(ICI, "sons")))
    ap.add_argument("--bind", default=os.environ.get("CUE_BIND", "127.0.0.1"))
    ap.add_argument("--banner", default=os.environ.get("CUE_BANNER", ""))
    a = ap.parse_args()
    with http.server.ThreadingHTTPServer((a.bind, a.port), creer_handler(a.audio, a.banner)) as httpd:
        print("Régie son sur http://%s:%d  (audio : %s)" % (a.bind, a.port, a.audio))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
