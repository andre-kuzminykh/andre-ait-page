# -*- coding: utf-8 -*-
"""NFR-SITE113 — заглушка публичного API партнёров продукта Andre AI для проверок сайта на столе.

Договорённость сайтов и продукта 26.11 (§2–§3). Продукт strategy.andre.technology отдаёт:

  GET  /api/partners/public?lang=ru|en → 200 {ok: true, partners: [...]} — формат partners/partners.json, только
       активные партнёры; без флага — пустой список;
  POST /api/partners/requests          → 201 {ok, id} — {partner_slug, name, email, company, message, lang};
  POST /api/partners/applications      → 201 {ok, id} — {name, email, linkedin, experience, rate_usd, lang};
       без флага — 404;

и открывает CORS двум адресам сайта (andre.technology, partners.andre.technology): GET, POST, OPTIONS. Заглушка
делает то же на 127.0.0.1 — сайт и она на разных портах, поэтому браузер проверяет CORS по-настоящему, с
предзапросом у POST с JSON. И ломается так, как может сломаться продукт:

  stub.mode       — каталог: "ok" | "empty" | "error" (500) | "slow" (ответ позже тайм-аута страницы) |
                    "nocors" (без Access-Control-Allow-Origin) | "badjson" | "notok" ({ok: false});
  stub.post_mode  — заявки: "ok" | "error" (500) | "off" (404, флаг выключен) | "nocors" (предзапрос без CORS) |
                    "notok" (200 {ok: false}) | "slow".

Страница партнёров берёт адрес продукта из строки window.AIT_API, если она задана до загрузки скрипта
(в Playwright — add_init_script); из адреса страницы он не подменяется.

    stub = ApiStub(origins=[site, sub])   # без origins — любой Origin
    stub.partners = [...]; stub.mode = "empty"
    stub.seen      # [(метод, путь, Origin, тело JSON или None)] — без предзапросов
    stub.preflights  # [(путь, Origin, запрошенные заголовки)] — предзапросы CORS (с перехватом запросов Playwright их не шлёт)
    stub.url       # http://127.0.0.1:N
    stub.stop()

Вручную — заглушка с примерами из partners.json на порту 8787 (любой Origin):

    python3 tools/api_stub.py [порт]
"""
import http.server
import json
import os
import socketserver
import sys
import threading
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = "/api/partners/public"
POSTS = ("/api/partners/requests", "/api/partners/applications")


class ApiStub:
    def __init__(self, origins=None, partners=None, delay=5.0, port=0):
        self.origins = set(origins) if origins else None
        self.partners = list(partners or [])
        self.mode, self.post_mode, self.delay = "ok", "ok", delay
        self.seen, self.preflights, self._ids, self._lock = [], [], 0, threading.Lock()
        stub = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _allow(self, mode):
                """CORS как у продукта: свой Origin — разрешён, чужой и режим nocors — без заголовка (браузер ответ не отдаст)."""
                origin = self.headers.get("Origin")
                if mode == "nocors" or not origin or (stub.origins is not None and origin not in stub.origins):
                    return
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")

            def _reply(self, code, body, mode):
                data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self._allow(mode)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)

            def _path(self):
                return urllib.parse.urlsplit(self.path).path

            def do_OPTIONS(self):
                mode = stub.post_mode if self._path() in POSTS else stub.mode
                with stub._lock:
                    stub.preflights.append((self._path(), self.headers.get("Origin"), self.headers.get("Access-Control-Request-Headers")))
                self.send_response(204)
                self._allow(mode)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Max-Age", "0")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self):
                path, mode = self._path(), stub.mode
                stub._note("GET", self.path, self.headers.get("Origin"), None)
                if path != PUBLIC:
                    return self._reply(404, {"ok": False, "error": "not found"}, mode)
                if mode == "slow":
                    time.sleep(stub.delay)
                if mode == "error":
                    return self._reply(500, {"ok": False, "error": "boom"}, mode)
                if mode == "badjson":
                    return self._reply(200, b"<html>not json</html>", mode)
                if mode == "notok":
                    return self._reply(200, {"ok": False}, mode)
                return self._reply(200, {"ok": True, "partners": [] if mode == "empty" else stub.partners}, mode)

            def do_POST(self):
                path, mode = self._path(), stub.post_mode
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                try:
                    body = json.loads(raw.decode("utf-8")) if raw else None
                except ValueError:
                    body = raw.decode("utf-8", "replace")
                stub._note("POST", path, self.headers.get("Origin"), body)
                if path not in POSTS or mode == "off":
                    return self._reply(404, {"ok": False, "error": "not found"}, mode)
                if mode == "slow":
                    time.sleep(stub.delay)
                if mode == "error":
                    return self._reply(500, {"ok": False, "error": "boom"}, mode)
                if mode == "notok":
                    return self._reply(200, {"ok": False, "error": "rejected"}, mode)
                with stub._lock:
                    stub._ids += 1
                    i = stub._ids
                return self._reply(201, {"ok": True, "id": i}, mode)

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

            def handle_error(self, *a):
                pass

        self._srv = Server(("127.0.0.1", port), Handler)
        self.url = "http://127.0.0.1:%d" % self._srv.server_address[1]
        threading.Thread(target=self._srv.serve_forever, daemon=True).start()

    def _note(self, method, path, origin, body):
        with self._lock:
            self.seen.append((method, path, origin, body))

    def posts(self, path=None):
        """Тела принятых POST (по пути, если задан)."""
        with self._lock:
            return [b for m, p, o, b in self.seen if m == "POST" and (path is None or p == path)]

    def reset(self, mode="ok", post_mode="ok"):
        with self._lock:
            self.seen, self.preflights = [], []
        self.mode, self.post_mode = mode, post_mode

    def stop(self):
        self._srv.shutdown()
        self._srv.server_close()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    with open(os.path.join(ROOT, "partners", "partners.json"), encoding="utf-8") as f:
        partners = json.load(f)
    stub = ApiStub(partners=partners, port=port)
    print("заглушка продукта: %s%s (на странице: window.AIT_API = '%s')" % (stub.url, PUBLIC, stub.url))
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        stub.stop()


if __name__ == "__main__":
    main()
