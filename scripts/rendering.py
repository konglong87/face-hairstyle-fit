"""Static, escaped, photo-free presentation; no network or executable report content."""
from html import escape
from typing import Dict

from scripts.contracts import Catalog


def text(value: str) -> str:
    return escape(value, quote=True)


def bullets(values) -> str:
    return "<ul>" + "".join("<li>" + text(v) + "</li>" for v in values) + "</ul>"


def style_label(recommendation: Dict, catalog: Catalog) -> str:
    ids = [recommendation[k] for k in ("family_id", "expression_id", "recipe_id")]
    return " · ".join(catalog.styles[key]["name"] for key in ids if key is not None)


def recommendation_html(recommendation: Dict, catalog: Catalog) -> str:
    modules = []
    names = {"hair": "发型", "makeup": "妆容（可选）", "outfit": "穿搭"}
    for key, module in recommendation["plan"].items():
        status = "已跳过" if module["status"] == "skip" else "可尝试"
        modules.append("<section><h3>" + names[key] + " · " + status + "</h3>"
                       + bullets(module["actions"]) + "<p>" + text(module["reason"]) + "</p></section>")
    return ("<article><h2>" + text(style_label(recommendation, catalog)) + "</h2><p>"
            + text(recommendation["rationale"]) + "</p><div class='modules'>"
            + "".join(modules) + "</div><h3>取舍</h3>" + bullets(recommendation["tradeoffs"])
            + "</article>")


def render_html(report: Dict, catalog: Catalog) -> str:
    observations = [o["description"] + " — " + o["evidence"] for o in report["observations"]]
    experiments = [e["action"] + " — " + e["why"] for e in report["experiments"]]
    status = {"ready": "建议可试", "provisional": "暂定建议", "needs_input": "需要补充照片"}[report["status"]]
    body = ("<main><header><p class='eyebrow'>FACE HAIRSTYLE FIT · " + status + "</p><h1>找到适合自己的风格</h1><p>"
            + text(report["summary"]) + "</p></header><article><h2>可见依据</h2>" + bullets(observations)
            + "</article>" + "".join(recommendation_html(r, catalog) for r in report["recommendations"])
            + "<article><h2>低成本试验</h2>" + bullets(experiments) + "<h2>尚未确认</h2>"
            + bullets(report["uncertainties"]) + "<h2>下一步</h2>" + bullets(report["questions"])
            + "<h2>边界</h2>" + bullets(report["limitations"]) + "</article></main>")
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Face Hairstyle Fit · 本地建议</title><style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f5f2eb;color:#262c29;font:16px/1.8 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:48px 24px}header{padding:0 4px 24px}h1{font-size:38px;line-height:1.3;margin:12px 0}
h2{font-size:24px;line-height:1.4}h3{font-size:18px;line-height:1.5}.eyebrow{letter-spacing:1px;color:#52665a;font-size:13px}
article{background:#fffefa;border:1px solid #deded3;border-radius:12px;padding:24px;margin:20px 0}
.modules{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}section{background:#f1f4ee;padding:16px;border-radius:8px}
p,li{overflow-wrap:anywhere}ul{padding-left:20px}li{margin:8px 0}@media(max-width:720px){.modules{grid-template-columns:1fr}main{padding:24px 16px}h1{font-size:30px}article{padding:18px}}
</style></head><body>""" + body + "</body></html>\n"
