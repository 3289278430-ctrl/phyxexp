"""统一数据识别层：文字 / 文档 / 图片 → 结构化数据表（全面覆盖）。

覆盖所有输入类型，每种用最合适的工具（不求每条路径精度均衡）：
  Excel(.xls/.xlsx) → xlrd / openpyxl
  CSV              → 标准库
  Word(.docx)      → python-docx
  PDF(有文字层)     → pypdf
  PDF(扫描)/图片    → OCR 后端（见 ocr_backend）
  纯文本/JSON      → 直接解析

OCR 后端分两档（见 README「数据识别」一节）：
  默认轻量 RapidOCR（pip install -r requirements-ingest.txt）
  选装高精度 PaddleOCR PP-Structure / Surya / TableTransformer（体积大，用户自装）
"""
import csv as _csv
import json
import os
import re


def ocr_backend():
    """检测可用 OCR 后端。默认轻量 RapidOCR；选装更重引擎可提表格结构/手写精度。"""
    try:
        import rapidocr_onnxruntime  # noqa: F401
        return "rapidocr"
    except ImportError:
        return None


def _rapidocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
        return RapidOCR()
    except ImportError:
        raise RuntimeError(
            "图片/扫描件识别需要 OCR 后端。轻量安装：pip install -r requirements-ingest.txt；"
            "高精度（表格结构/手写/公式）选装：pip install paddleocr paddlepaddle"
        )


def _load_image(path):
    if path.lower().endswith(".pdf"):
        import tempfile
        from pypdf import PdfReader
        best = None
        for pg in PdfReader(path).pages:
            for im in pg.images:
                if best is None or len(im.data) > len(best.data):
                    best = im
        if best is None:
            raise ValueError("PDF 中没有可识别的图片")
        ext = ".jpg" if best.data[:3] == b"\xff\xd8\xff" else ".png"
        tmp = os.path.join(tempfile.gettempdir(), "phyxexp_ingest" + ext)
        with open(tmp, "wb") as f:
            f.write(best.data)
        return tmp
    return path


def ocr_lines(path):
    result, _ = _rapidocr()(_load_image(path))
    lines = []
    if result:
        for box, text, score in result:
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            lines.append((sum(xs) / 4.0, sum(ys) / 4.0, str(text).strip(), float(score)))
    return lines


def lines_to_grid(lines, y_gap=18.0):
    rows = []
    for cx, cy, text, sc in sorted(lines, key=lambda t: t[1]):
        for r in rows:
            if abs(cy - r["cy"]) <= y_gap:
                r["cells"].append((cx, text, sc))
                break
        else:
            rows.append({"cy": cy, "cells": [(cx, text, sc)]})
    grid = []
    for r in rows:
        r["cells"].sort(key=lambda t: t[0])
        grid.append([t for (cx, t, sc) in r["cells"]])
    return grid


def numeric_columns(grid):
    ncols = max((len(r) for r in grid), default=0)
    out = []
    for c in range(ncols):
        vals = [r[c] for r in grid if c < len(r)]
        n = 0
        for v in vals:
            try:
                float(str(v).replace(",", ".").replace("，", "."))
                n += 1
            except Exception:
                pass
        if n >= max(2, len(vals) * 0.5):
            out.append(c)
    return out


def _clean_rows(rows):
    return [r for r in rows if any(str(v).strip() not in ("", "None") for v in r)]


def read_excel(path):
    ext = path.lower().rsplit(".", 1)[-1]
    tables = []
    if ext == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        for ws in wb.worksheets:
            rows = [list(r) for r in ws.iter_rows(values_only=True)]
            rows = _clean_rows(rows)
            if rows:
                tables.append({"sheet": ws.title, "rows": rows})
    else:  # xls
        import xlrd
        wb = xlrd.open_workbook(path)
        for sh in wb.sheets():
            rows = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
            rows = _clean_rows(rows)
            if rows:
                tables.append({"sheet": sh.name, "rows": rows})
    return tables


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(_csv.reader(f))
    return [{"sheet": os.path.basename(path), "rows": _clean_rows(rows)}]


def read_docx(path):
    import docx
    d = docx.Document(path)
    tables = []
    for i, t in enumerate(d.tables):
        rows = [[c.text.strip() for c in row.cells] for row in t.rows]
        tables.append({"sheet": f"table{i + 1}", "rows": rows})
    return tables


def read_pdf(path):
    from pypdf import PdfReader
    texts = [(pg.extract_text() or "").strip() for pg in PdfReader(path).pages]
    if any(texts):
        rows = [ln.split() for ln in "\n".join(texts).split("\n") if ln.strip()]
        return [{"sheet": "pdf-text", "rows": rows}]
    return [{"sheet": "pdf-scan", "rows": lines_to_grid(ocr_lines(path))}]


def parse_text(text):
    rows = []
    for ln in text.splitlines():
        nums = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", ln)
        if nums:
            rows.append(nums)
    return [{"sheet": "text", "rows": rows}]


def ingest(source):
    """统一入口：自动判断输入类型，返回 {"source_type", "ocr_backend", "tables"}。"""
    backend = ocr_backend()
    if isinstance(source, str) and os.path.exists(source):
        ext = source.lower().rsplit(".", 1)[-1] if "." in source else ""
        if ext in ("xls", "xlsx"):
            return {"source_type": "excel(" + ext + ")", "ocr_backend": backend, "tables": read_excel(source)}
        if ext == "csv":
            return {"source_type": "csv", "ocr_backend": backend, "tables": read_csv(source)}
        if ext == "docx":
            return {"source_type": "docx", "ocr_backend": backend, "tables": read_docx(source)}
        if ext == "pdf":
            return {"source_type": "pdf", "ocr_backend": backend, "tables": read_pdf(source)}
        if ext in ("png", "jpg", "jpeg", "webp", "bmp", "gif"):
            return {"source_type": "image(" + ext + ")", "ocr_backend": backend,
                    "tables": [{"sheet": "image", "rows": lines_to_grid(ocr_lines(source))}]}
    if isinstance(source, str):
        try:
            obj = json.loads(source)
            if isinstance(obj, dict):
                return {"source_type": "json", "ocr_backend": backend,
                        "tables": [{"sheet": "json", "rows": [[k, v] for k, v in obj.items()]}]}
        except Exception:
            pass
        return {"source_type": "text", "ocr_backend": backend, "tables": parse_text(source)}
    return {"source_type": "unknown", "ocr_backend": backend, "tables": []}
