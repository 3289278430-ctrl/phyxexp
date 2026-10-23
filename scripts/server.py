#!/usr/bin/env python3
"""phyxexp HTTP 入口 —— 供 ChatGPT Custom GPT 的 Actions 调用（受约束、零依赖）。

启动：python scripts/server.py [--port 8000] [--host 127.0.0.1]
端点：
  GET  /health    健康检查
  GET  /list      列出可配置实验（字段见各实验 inputs）
  POST /run       body {"experiment": "<id>", "data": {...}} -> 带溯源的结构化结果

说明：ChatGPT Actions 需要公网 HTTPS，本地开发可先用 curl 验证，
真实接入用 ngrok 暴露本端口（见 docs/ChatGPT接入.md）。
"""
import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phyxexp.agent import Conductor, GuardError
from phyxexp.config import load_config, find_experiment

CONFIG = load_config()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "service": "phyxexp",
                             "standard": CONFIG["defaults"]["uncertainty_standard"]})
        elif self.path == "/list":
            self._send(200, {
                "standard": CONFIG["defaults"]["uncertainty_standard"],
                "experiments": [
                    {"id": e["id"], "name": e["name"], "tool": e["tool"],
                     "inputs": e["inputs"], "checks": e.get("checks", [])}
                    for e in CONFIG["experiments"]
                ],
            })
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/run":
            self._send(404, {"error": "not found"})
            return
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(n) if n else b"{}"
            payload = json.loads(raw.decode("utf-8"))
            exp = find_experiment(CONFIG, payload.get("experiment"))
            data = payload.get("data", {})
            res = Conductor(CONFIG).solve_experiment(exp, data)
            self._send(200, {
                "experiment": {"id": exp["id"], "name": exp["name"], "tool": exp["tool"]},
                "run_id": res.record.run_id,
                "input_hash": res.record.input_hash,
                "standard": CONFIG["defaults"]["uncertainty_standard"],
                "checks": res.checks,
                "conclusion": res.conclusion,
                "grounded": res.grounded,
                "replay_match": res.replay_match,
            })
        except GuardError as e:
            self._send(403, {"error": "约束被违反: " + str(e)})
        except Exception as e:
            self._send(400, {"error": str(e)})

    def log_message(self, *args):  # 静音访问日志
        pass


def main():
    ap = argparse.ArgumentParser(description="phyxexp 受约束实验数据处理 HTTP 服务")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    print(f"phyxexp 服务: http://{args.host}:{args.port}")
    print("端点: GET /list, POST /run  |  ChatGPT Actions 用 chatgpt/openapi.json")
    HTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
