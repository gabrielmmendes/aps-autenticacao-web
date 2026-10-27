"""Monta o documento da APS (HTML -> PDF) a partir de conteudo.html.

Macros aceitas no conteúdo:
  [[c:chave]]          citação entre parênteses, com link para a referência
  [[c:ch1;ch2]]        citação múltipla
  [[t:chave]]          citação narrativa: Autor (ano)
  [[fig:id]] [[tab:id]] referência numerada a figura/tabela, com link
  [[sec:id]]           referência a item/seção (texto "item X.Y"), com link
  [[aut:X.Y]] [[rev:X.Y]] nome do autor/revisor do item
  <div class="meta" data-item="X.Y"></div>  bloco de autoria/revisão do item
"""
import re, csv, html, pathlib, sys
import weasyprint

BASE = pathlib.Path(__file__).parent
G, K = "Gabriel Matos Mendes", "Kezer dos Santos Souza"
AUTORES = sorted([G, K])
REPOSITORIO = "https://github.com/gabrielmmendes/aps-autenticacao-web"

# Item de informação -> (autor, revisor). Regra 7: autor ≠ revisor; ambos autores e revisores.
ITENS = {
    "P.1": ("Apresentação e organização do documento", K, G),
    "P.2": ("Nota sobre o uso de inteligência artificial", G, K),
    "1.1": ("Visão geral do ambiente operacional", G, K),
    "1.2": ("Softwares de apoio: papel, invocação e resultados", K, G),
    "1.3": ("Processamento de uma requisição Web de ponta a ponta", G, K),
    "1.4": ("Processamento no navegador", K, G),
    "1.5": ("Processamento no servidor web, no servidor de aplicação e no SGBD", G, K),
    "2.1": ("Requisitos e escopo da solução", K, G),
    "2.2": ("Decisões arquiteturais", G, K),
    "2.3": ("Visões de contexto e de contêineres", K, G),
    "2.4": ("Visão de componentes", G, K),
    "2.5": ("Especificação da interface (API)", K, G),
    "2.6": ("Modelo de dados", G, K),
    "2.7": ("Desenho detalhado dos componentes", K, G),
    "2.8": ("Comportamento dinâmico da autenticação", G, K),
    "2.9": ("Implantação e configuração do ambiente operacional", K, G),
    "2.10": ("Rastreabilidade entre requisitos, projeto e ambiente", G, K),
    "A": ("Apêndice A – Registro de comunicações e reuniões", G, K),
    "B": ("Apêndice B – Gerência de configuração no GitHub", K, G),
    "C": ("Apêndice C – Planejamento do trabalho e gestão de riscos da equipe", G, K),
}
ANCORA = {k: ("i" + k.replace(".", "-")) for k in ITENS}
ANCORA.update({"P.1": "apresentacao", "P.2": "nota-ia", "A": "apendice-a", "B": "apendice-b", "C": "apendice-c"})

# Referências (ABNT NBR 6023:2018). chave -> (citação, texto completo)
REFS = {
 "anthropic": ("ANTHROPIC, 2026", "ANTHROPIC. <b>Claude Opus 5.5</b>: modelo de linguagem de grande escala. San Francisco: Anthropic, 2026. Assistente de IA utilizado na elaboração deste documento. Disponível em: https://claude.ai. Acesso em: 27 out. 2026."),
 "bass": ("BASS; CLEMENTS; KAZMAN, 2021", "BASS, L.; CLEMENTS, P.; KAZMAN, R. <b>Software architecture in practice</b>. 4. ed. Boston: Addison-Wesley, 2021."),
 "rfc9106": ("BIRYUKOV <i>et al.</i>, 2021", "BIRYUKOV, A.; DINU, D.; KHOVRATOVICH, D.; JOSEFSSON, S. <b>RFC 9106</b>: Argon2 memory-hard function for password hashing and proof-of-work applications. [<i>S. l.</i>]: IRTF, set. 2021. DOI: 10.17487/RFC9106."),
 "rfc8259": ("BRAY, 2017", "BRAY, T. (ed.). <b>RFC 8259</b>: The JavaScript Object Notation (JSON) data interchange format. [<i>S. l.</i>]: IETF, dez. 2017. DOI: 10.17487/RFC8259."),
 "c4": ("BROWN, 2026", "BROWN, S. <b>The C4 model for visualising software architecture</b>. [<i>S. l.</i>], 2026. Disponível em: https://c4model.com. Acesso em: 27 out. 2026."),
 "jakarta": ("ECLIPSE FOUNDATION, 2022", "ECLIPSE FOUNDATION. <b>Jakarta Servlet Specification</b>: version 6.0. Ottawa: Eclipse Foundation, 2022. Disponível em: https://jakarta.ee/specifications/servlet/6.0/. Acesso em: 27 out. 2026."),
 "fielding2000": ("FIELDING, 2000", "FIELDING, R. T. <b>Architectural styles and the design of network-based software architectures</b>. 2000. Tese (Doutorado em Ciência da Informação e da Computação) – University of California, Irvine, 2000."),
 "rfc9110": ("FIELDING; NOTTINGHAM; RESCHKE, 2022a", "FIELDING, R.; NOTTINGHAM, M.; RESCHKE, J. (ed.). <b>RFC 9110</b>: HTTP semantics. [<i>S. l.</i>]: IETF, jun. 2022a. DOI: 10.17487/RFC9110."),
 "rfc9112": ("FIELDING; NOTTINGHAM; RESCHKE, 2022b", "FIELDING, R.; NOTTINGHAM, M.; RESCHKE, J. (ed.). <b>RFC 9112</b>: HTTP/1.1. [<i>S. l.</i>]: IETF, jun. 2022b. DOI: 10.17487/RFC9112."),
 "fowler": ("FOWLER, 2002", "FOWLER, M. <b>Patterns of enterprise application architecture</b>. Boston: Addison-Wesley, 2002."),
 "grigorik": ("GRIGORIK, 2013", "GRIGORIK, I. <b>High performance browser networking</b>. Sebastopol: O'Reilly, 2013."),
 "rfc6797": ("HODGES; JACKSON; BARTH, 2012", "HODGES, J.; JACKSON, C.; BARTH, A. <b>RFC 6797</b>: HTTP Strict Transport Security (HSTS). [<i>S. l.</i>]: IETF, nov. 2012. DOI: 10.17487/RFC6797."),
 "iso12207": ("ISO/IEC/IEEE, 2026", "INTERNATIONAL ORGANIZATION FOR STANDARDIZATION; INTERNATIONAL ELECTROTECHNICAL COMMISSION; INSTITUTE OF ELECTRICAL AND ELECTRONICS ENGINEERS. <b>ISO/IEC/IEEE 12207:2026</b>: systems and software engineering – software life cycle processes. Genebra: ISO, 2026."),
 "iso25010": ("ISO/IEC, 2023", "INTERNATIONAL ORGANIZATION FOR STANDARDIZATION; INTERNATIONAL ELECTROTECHNICAL COMMISSION. <b>ISO/IEC 25010:2023</b>: systems and software engineering – systems and software quality requirements and evaluation (SQuaRE) – product quality model. Genebra: ISO, 2023."),
 "kurose": ("KUROSE; ROSS, 2021", "KUROSE, J. F.; ROSS, K. W. <b>Redes de computadores e a Internet</b>: uma abordagem <i>top-down</i>. 8. ed. São Paulo: Pearson, 2021."),
 "martin": ("MARTIN, 2019", "MARTIN, R. C. <b>Arquitetura limpa</b>: o guia do artesão para estrutura e design de software. Rio de Janeiro: Alta Books, 2019."),
 "rfc1034": ("MOCKAPETRIS, 1987", "MOCKAPETRIS, P. <b>RFC 1034</b>: domain names – concepts and facilities. [<i>S. l.</i>]: IETF, nov. 1987. DOI: 10.17487/RFC1034."),
 "nginx": ("NGINX, 2026", "NGINX. <b>nginx documentation</b>. [<i>S. l.</i>]: F5, 2026. Disponível em: https://nginx.org/en/docs/. Acesso em: 27 out. 2026."),
 "rfc9457": ("NOTTINGHAM; WILDE; DALAL, 2023", "NOTTINGHAM, M.; WILDE, E.; DALAL, S. <b>RFC 9457</b>: problem details for HTTP APIs. [<i>S. l.</i>]: IETF, jul. 2023. DOI: 10.17487/RFC9457."),
 "uml": ("OMG, 2017", "OBJECT MANAGEMENT GROUP. <b>OMG Unified Modeling Language (OMG UML)</b>: version 2.5.1. Needham: OMG, 2017. Disponível em: https://www.omg.org/spec/UML/2.5.1. Acesso em: 27 out. 2026."),
 "owasp_auth": ("OWASP, 2026a", "OWASP FOUNDATION. <b>Authentication cheat sheet</b>. [<i>S. l.</i>]: OWASP, 2026a. Disponível em: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html. Acesso em: 27 out. 2026."),
 "owasp_pwd": ("OWASP, 2026b", "OWASP FOUNDATION. <b>Password storage cheat sheet</b>. [<i>S. l.</i>]: OWASP, 2026b. Disponível em: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html. Acesso em: 27 out. 2026."),
 "postgres": ("POSTGRESQL GLOBAL DEVELOPMENT GROUP, 2026", "POSTGRESQL GLOBAL DEVELOPMENT GROUP. <b>PostgreSQL documentation</b>. [<i>S. l.</i>], 2026. Disponível em: https://www.postgresql.org/docs/current/. Acesso em: 27 out. 2026."),
 "pressman": ("PRESSMAN; MAXIM, 2021", "PRESSMAN, R. S.; MAXIM, B. R. <b>Engenharia de software</b>: uma abordagem profissional. 9. ed. Porto Alegre: AMGH, 2021."),
 "rfc8446": ("RESCORLA, 2018", "RESCORLA, E. <b>RFC 8446</b>: the Transport Layer Security (TLS) protocol version 1.3. [<i>S. l.</i>]: IETF, ago. 2018. DOI: 10.17487/RFC8446."),
 "sommerville": ("SOMMERVILLE, 2019", "SOMMERVILLE, I. <b>Engenharia de software</b>. 10. ed. São Paulo: Pearson, 2019."),
 "spring": ("SPRING, 2026", "SPRING. <b>Spring Framework reference documentation</b>. [<i>S. l.</i>]: Broadcom, 2026. Disponível em: https://docs.spring.io/spring-framework/reference/. Acesso em: 27 out. 2026."),
 "nist": ("TEMOSHOK <i>et al.</i>, 2025", "TEMOSHOK, D. <i>et al.</i> <b>Digital identity guidelines</b>: authentication and authenticator management. Gaithersburg: National Institute of Standards and Technology, jul. 2025. (NIST Special Publication 800-63B-4). DOI: 10.6028/NIST.SP.800-63B-4."),
 "tomcat": ("APACHE SOFTWARE FOUNDATION, 2026", "APACHE SOFTWARE FOUNDATION. <b>Apache Tomcat documentation</b>. Wilmington: ASF, 2026. Disponível em: https://tomcat.apache.org/. Acesso em: 27 out. 2026."),
 "rfc9113": ("THOMSON; BENFIELD, 2022", "THOMSON, M.; BENFIELD, C. (ed.). <b>RFC 9113</b>: HTTP/2. [<i>S. l.</i>]: IETF, jun. 2022. DOI: 10.17487/RFC9113."),
 "whatwg_html": ("WHATWG, 2026a", "WHATWG. <b>HTML living standard</b>. [<i>S. l.</i>]: WHATWG, 2026a. Disponível em: https://html.spec.whatwg.org/. Acesso em: 27 out. 2026."),
 "whatwg_fetch": ("WHATWG, 2026b", "WHATWG. <b>Fetch living standard</b>. [<i>S. l.</i>]: WHATWG, 2026b. Disponível em: https://fetch.spec.whatwg.org/. Acesso em: 27 out. 2026."),
}


def narrativa(cit):
    """'FIELDING; NOTTINGHAM; RESCHKE, 2022a' -> 'Fielding, Nottingham e Reschke (2022a)'"""
    nomes, ano = cit.rsplit(", ", 1)
    partes = [p.strip() for p in nomes.split(";")]
    def cap(n):
        if n.startswith("<") or n.isupper() and len(n) <= 6 or "/" in n:
            return n
        return " ".join(w if w in ("<i>et", "al.</i>") else w.capitalize() for w in n.split(" "))
    partes = [cap(p) for p in partes]
    txt = partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " e " + partes[-1]
    return f"{txt} ({ano})"


def main():
    src = (BASE / "conteudo.html").read_text(encoding="utf-8")
    usadas = set()

    def cit(m):
        ks = m.group(1).split(";")
        out = []
        for k in ks:
            if k not in REFS:
                sys.exit(f"referência desconhecida: {k}")
            usadas.add(k)
            out.append(f'<a class="cit" href="#ref-{k}">{REFS[k][0]}</a>')
        return "(" + "; ".join(out) + ")"
    src = re.sub(r"\[\[c:([^\]]+)\]\]", cit, src)

    def narr(m):
        k = m.group(1); usadas.add(k)
        return f'<a class="cit" href="#ref-{k}">{narrativa(REFS[k][0])}</a>'
    src = re.sub(r"\[\[t:([^\]]+)\]\]", narr, src)

    # figuras
    figs, tabs = {}, {}
    def fig(m):
        attrs = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(1)))
        n = len(figs) + 1; figs[attrs["id"]] = (n, attrs["titulo"])
        return (f'<figure id="{attrs["id"]}"><p class="cap">Figura {n} – {attrs["titulo"]}</p>'
                f'<img src="build/fig/{attrs["src"]}" style="width:{attrs.get("w","16cm")}"/>'
                f'<p class="fonte">Fonte: {attrs.get("fonte","elaborada pelos autores")}.</p></figure>')
    src = re.sub(r"<fig ([^>]*)/>", fig, src)

    def tab(m):
        attrs = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(1)))
        n = len(tabs) + 1; tabs[attrs["id"]] = (n, attrs["titulo"])
        cls = attrs.get("class", "")
        return (f'<p class="cap tcap" id="{attrs["id"]}">Tabela {n} – {attrs["titulo"]}</p>'
                f'<table class="{cls}">')
    src = re.sub(r"<tab ([^>]*)>", tab, src)
    src = re.sub(r'</tab fonte="([^"]*)">', lambda m: f'</table><p class="fonte">Fonte: {m.group(1)}.</p>', src)
    src = src.replace("</tab>", '</table><p class="fonte">Fonte: elaborada pelos autores.</p>')

    def ref(m):
        tipo, k = m.group(1), m.group(2)
        d = figs if tipo == "fig" else tabs
        if k not in d:
            sys.exit(f"{tipo} desconhecida: {k}")
        return f'<a class="xref" href="#{k}">{"Figura" if tipo=="fig" else "Tabela"} {d[k][0]}</a>'
    src = re.sub(r"\[\[(fig|tab):([^\]]+)\]\]", ref, src)

    def sec(m):
        k = m.group(1)
        rot = {"A": "Apêndice A", "B": "Apêndice B", "C": "Apêndice C", "P.2": "Nota sobre o uso de IA", "P.1": "Apresentação",
               "1": "Seção 1", "2": "Seção 2", "refs": "Referências"}.get(k, f"item {k}")
        anc = {"1": "secao-1", "2": "secao-2", "refs": "referencias"}.get(k, ANCORA.get(k))
        return f'<a class="xref" href="#{anc}">{rot}</a>'
    src = re.sub(r"\[\[sec:([^\]]+)\]\]", sec, src)

    src = re.sub(r"\[\[aut:([^\]]+)\]\]", lambda m: ITENS[m.group(1)][1], src)
    src = re.sub(r"\[\[rev:([^\]]+)\]\]", lambda m: ITENS[m.group(1)][2], src)

    def meta(m):
        k = m.group(1); _, a, r = ITENS[k]
        return (f'<div class="meta"><span><b>Item de informação {k if k[0] not in "PABC" else ""}</b></span>'
                f'<span>Autoria: {a}</span><span>Revisão: {r}</span>'
                f'<span>Apoio de IA: <a href="#nota-ia">ver Nota</a></span></div>')
    src = re.sub(r'<div class="meta" data-item="([^"]+)"></div>', meta, src)

    # quadro de autoria
    linhas = "".join(f'<tr><td><a href="#{ANCORA[k]}">{k if k[0] not in "PABC" else "–"}</a></td><td>{t}</td><td>{a}</td><td>{r}</td></tr>'
                     for k, (t, a, r) in ITENS.items())
    src = src.replace("<!--QUADRO_AUTORIA-->", linhas)
    resumo = "".join(f"<tr><td>{p}</td><td>{sum(1 for v in ITENS.values() if v[1]==p)}</td><td>{sum(1 for v in ITENS.values() if v[2]==p)}</td></tr>" for p in AUTORES)
    src = src.replace("<!--RESUMO_AUTORIA-->", resumo)
    src = src.replace("<!--AUTORES-->", "<br/>".join(AUTORES))
    src = src.replace("<!--REPOSITORIO-->", REPOSITORIO)

    # listas de figuras e tabelas
    lf = "".join(f'<li><a href="#{k}">Figura {n} – {t}</a></li>' for k, (n, t) in figs.items())
    lt = "".join(f'<li><a href="#{k}">Tabela {n} – {t}</a></li>' for k, (n, t) in tabs.items())
    src = src.replace("<!--LISTA_FIGURAS-->", lf).replace("<!--LISTA_TABELAS-->", lt)

    # registros de comunicação (Apêndice A) a partir de CSV
    with open(BASE / "registros_comunicacao.csv", encoding="utf-8") as f:
        regs = list(csv.DictReader(f))
    lin = "".join("<tr>" + "".join(f"<td>{html.escape(r[c])}</td>" for c in ("data", "meio", "participantes", "assunto", "evidencia")) + "</tr>" for r in regs)
    src = src.replace("<!--REGISTROS-->", lin)

    # referências: só as citadas, em ordem alfabética da forma de citação
    nao_citadas = set(REFS) - usadas
    if nao_citadas:
        print("AVISO – referências não citadas (omitidas):", sorted(nao_citadas))
    ordem = sorted(usadas, key=lambda k: re.sub("<[^>]+>", "", REFS[k][1]).upper())
    src = src.replace("<!--REFERENCIAS-->", "".join(f'<p class="ref" id="ref-{k}">{REFS[k][1]}</p>' for k in ordem))

    css = (BASE / "estilo.css").read_text(encoding="utf-8")
    doc = f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>APS – Software Web para Autenticação de Usuários</title>' \
          f'<meta name="author" content="{"; ".join(AUTORES)}"><style>{css}</style></head><body>{src}</body></html>'
    (BASE / "build" / "documento.html").write_text(doc, encoding="utf-8")
    weasyprint.HTML(string=doc, base_url=str(BASE)).write_pdf(BASE / "build" / "APS_Autenticacao_Web.pdf")
    print(f"ok: {len(figs)} figuras, {len(tabs)} tabelas, {len(usadas)} referências")


if __name__ == "__main__":
    main()
