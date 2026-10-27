"""Gerador minimalista de diagramas de sequência (notação UML simplificada) em SVG."""
from xml.sax.saxutils import escape

FONT = "Liberation Sans"


def sequence(participants, steps, width=900, col_gap=None, title=None, step_h=30, top=70):
    """participants: lista de (id, rotulo multilinha com \\n, estilo)
    steps: lista de tuplas:
      ("msg", origem, destino, texto, tracejado:bool)
      ("self", ator, texto)
      ("note", ator_ini, ator_fim, texto)
      ("frame", rotulo, texto_condicao)  -> inicia fragmento
      ("else", texto_condicao)
      ("endframe",)
    """
    n = len(participants)
    margin = 70
    gap = (width - 2 * margin) / (n - 1)
    xs = {p[0]: margin + i * gap for i, p in enumerate(participants)}
    out = []
    y = top + 20
    frames = []
    body = []
    for st in steps:
        kind = st[0]
        if kind == "msg":
            _, a, b, text, dashed = st
            x1, x2 = xs[a], xs[b]
            y += step_h
            dash = ' stroke-dasharray="5,4"' if dashed else ""
            body.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#222" stroke-width="1.2"{dash} marker-end="url(#arr{"o" if dashed else ""})"/>')
            tx = (x1 + x2) / 2
            body.append(f'<text x="{tx}" y="{y-5}" font-size="11.5" text-anchor="middle" font-family="{FONT}">{escape(text)}</text>')
        elif kind == "self":
            _, a, text = st
            x = xs[a]
            y += step_h
            body.append(f'<path d="M{x},{y-8} h28 v14 h-26" fill="none" stroke="#222" stroke-width="1.2" marker-end="url(#arr)"/>')
            if x + 34 + len(text) * 6.4 > width - 4:
                body.append(f'<text x="{x-6}" y="{y+3}" font-size="11.5" text-anchor="end" font-family="{FONT}">{escape(text)}</text>')
            else:
                body.append(f'<text x="{x+34}" y="{y+3}" font-size="11.5" font-family="{FONT}">{escape(text)}</text>')
            y += 6
        elif kind == "note":
            _, a, b, text = st
            x1, x2 = min(xs[a], xs[b]) - 40, max(xs[a], xs[b]) + 40
            lines = text.split("\n")
            y += 10
            h = 14 * len(lines) + 8
            body.append(f'<rect x="{x1}" y="{y}" width="{x2-x1}" height="{h}" fill="#fff7d6" stroke="#b59a3a"/>')
            for i, ln in enumerate(lines):
                body.append(f'<text x="{(x1+x2)/2}" y="{y+15+i*14}" font-size="10" text-anchor="middle" font-family="{FONT}" font-style="italic">{escape(ln)}</text>')
            y += h
        elif kind == "frame":
            _, label, cond = st
            y += 18
            frames.append([label, y, [(cond, y)]])
        elif kind == "else":
            y += 14
            frames[-1][2].append((st[1], y))
        elif kind == "endframe":
            label, y0, parts = frames.pop()
            y += 12
            fx1, fx2 = margin - 55, width - margin + 55
            body.insert(0, f'<rect x="{fx1}" y="{y0-12}" width="{fx2-fx1}" height="{y-y0+12}" fill="none" stroke="#5470a8" stroke-width="1"/>')
            body.append(f'<path d="M{fx1},{y0-12} h46 v12 l-6,6 h-40 z" fill="#e3e9f6" stroke="#5470a8"/>')
            body.append(f'<text x="{fx1+5}" y="{y0+1}" font-size="10" font-weight="bold" font-family="{FONT}">{escape(label)}</text>')
            for i, (cond, cy) in enumerate(parts):
                if i > 0:
                    body.append(f'<line x1="{fx1}" y1="{cy-6}" x2="{fx2}" y2="{cy-6}" stroke="#5470a8" stroke-dasharray="6,4"/>')
                body.append(f'<text x="{fx1+56 if i==0 else fx1+6}" y="{cy+ (1 if i==0 else 6)}" font-size="10" font-family="{FONT}" fill="#2c3f6b">[{escape(cond)}]</text>')
    total_h = y + 40
    # cabeçalhos e linhas de vida
    for pid, label, style in participants:
        x = xs[pid]
        lines = label.split("\n")
        w = max(len(l) for l in lines) * 6.8 + 16
        h = 14 * len(lines) + 10
        fill = {"ator": "#ffffff", "cliente": "#e8f0fb", "infra": "#eef6ea", "app": "#fbefe2", "dados": "#f3e9f7"}.get(style, "#f2f2f2")
        out.append(f'<line x1="{x}" y1="{top + h - 18}" x2="{x}" y2="{total_h-10}" stroke="#888" stroke-dasharray="4,4"/>')
        if style == "ator":
            cy = top - 12
            out.append(f'<circle cx="{x}" cy="{cy-14}" r="7" fill="#fff" stroke="#222"/>'
                       f'<path d="M{x},{cy-7} v14 M{x-10},{cy} h20 M{x},{cy+7} l-8,10 M{x},{cy+7} l8,10" stroke="#222" fill="none"/>')
            out.append(f'<text x="{x}" y="{cy+30}" font-size="11.5" text-anchor="middle" font-family="{FONT}" font-weight="bold">{escape(label)}</text>')
        else:
            out.append(f'<rect x="{x-w/2}" y="{top-28}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="#333"/>')
            for i, ln in enumerate(lines):
                out.append(f'<text x="{x}" y="{top-12+i*14}" font-size="11.5" text-anchor="middle" font-family="{FONT}" font-weight="bold">{escape(ln)}</text>')
    defs = ('<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
            '<path d="M0,0 L10,4 L0,8 z" fill="#222"/></marker>'
            '<marker id="arro" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
            '<path d="M0,0 L10,4 L0,8" fill="none" stroke="#222"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}">'
            + defs + '<rect width="100%" height="100%" fill="white"/>' + "".join(out) + "".join(body) + "</svg>")
