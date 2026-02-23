# -*- coding: utf-8 -*-
import os, json
try:
    import yaml
except Exception:
    yaml = None

HERE = os.path.dirname(os.path.abspath(__file__))
YAML_PATH = os.path.join(HERE, "thoth_oracle_output.yaml")
PDF_PATH  = os.path.join(HERE, "Thoth_Oracle_Output_JP.pdf")

def load_yaml(path=YAML_PATH):
    if yaml is None:
        # 極小依存：yamlが無い環境でも動くよう軽量パーサを用意（キーだけ拾う簡易版）
        data = {}
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        data["RAW"] = content
        return data
    with open(path, "r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)

def render_text(data):
    if "RAW" in data:
        return data["RAW"]
    def jget(d,k,default=""):
        return d.get(k, default) if isinstance(d, dict) else default
    lines = []
    lines.append("【泉珠コア・トート神託モードF（融合）】")
    lines.append(f"ModeID: {jget(data,'ModeID')}")
    lines.append(f"Purpose: {jget(data,'Purpose')}")
    lines.append("")
    for key in ["CREATE_LAYER","WISDOM_LAYER","FUSION_LAYER","SYMBOLIC_LAYER"]:
        layer = jget(data, key, {})
        title = jget(layer,"Title", key)
        symbol = jget(layer,"Symbol","")
        lines.append("――――――――――――――――――――")
        lines.append(f"[{symbol}] {title}")
        ess = jget(layer,"Essence","")
        if ess: lines.append(f"Essence: {ess}")
        for sect in ["Structure","Spirit","Integration"]:
            if sect in layer:
                lines.append(sect + ":")
                for s in layer[sect]:
                    lines.append("  - " + s)
        eq = jget(layer,"Equation","")
        if eq: lines.append(f"Equation: {eq}")
        o = jget(layer,"Oracle","")
        if o: lines.append(f"Oracle: {o}")
        e = jget(layer,"Encoded","")
        if e: lines.append(f"Encoded: {e}")
        out = jget(layer,"Output","")
        if out: lines.append(f"Output: {out}")
        lines.append("")
    return "\n".join(lines)

def write_pdf(text, pdf_path=PDF_PATH):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica", 11)
        x, y = 40, height - 40
        for line in text.split("\n"):
            c.drawString(x, y, line[:120])
            y -= 16
            if y < 40:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 40
        c.save()
        return True
    except Exception as e:
        # フォールバック: シンプルなバイナリPDFプレースホルダ
        with open(pdf_path, "wb") as fp:
            fp.write(b"%PDF-1.4\n% placeholder\n")
        return False

def generate_oracle(mode="fusion"):
    data = load_yaml()
    text = render_text(data)
    ok = write_pdf(text, PDF_PATH)
    return {"ok": ok, "pdf": PDF_PATH, "text_preview": text[:300]}

if __name__ == "__main__":
    print(json.dumps(generate_oracle(), ensure_ascii=False, indent=2))
