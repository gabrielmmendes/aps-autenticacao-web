"""Gera todas as figuras do documento (SVG) a partir de fontes Graphviz e do gerador de sequência."""
import subprocess, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from seq import sequence

OUT = pathlib.Path(__file__).parent.parent / "build" / "fig"
OUT.mkdir(parents=True, exist_ok=True)
F = 'fontname="Liberation Sans"'


def dot(name, src):
    svg = subprocess.run(["dot", "-Tsvg"], input=src.encode(), capture_output=True, check=True).stdout
    (OUT / f"{name}.svg").write_bytes(svg)


# ---------------------------------------------------------------- Seção 1
dot("f1_ambiente", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=11 nodesep=0.25 ranksep=0.3 compound=true];
 node[{F} fontsize=10 shape=box style="rounded,filled" fillcolor="#ffffff"]; edge[{F} fontsize=9];
 usuario[label="Usuário" shape=plaintext fillcolor=none];
 subgraph cluster_cli {{ label="Estação do usuário (lado cliente)"; style="rounded,filled"; fillcolor="#e8f0fb"; color="#7d97c2";
   subgraph cluster_nav {{ label="Navegador Web"; style="rounded,filled"; fillcolor="#f5f8fd";
     ui[label="Interface do\\nnavegador"]; {{rank=same; render; js; rede;}} render[label="Motor de\\nrenderização\\n(HTML/CSS)"]; js[label="Motor\\nJavaScript"]; rede[label="Pilha de rede\\n(HTTP, TLS,\\ncache)"]; }}
   socli[label="Sistema operacional\\n(sockets TCP/UDP,\\nresolvedor DNS local)" fillcolor="#dde6f5"]; }}
 subgraph cluster_net {{ label="Internet"; style="rounded,dashed"; color="#999999";
   dns[label="Servidores DNS\\n(recursivo e\\nautoritativo)" fillcolor="#f2f2f2"]; }}
 subgraph cluster_srv {{ label="Infraestrutura do provedor (lado servidor)"; style="rounded,filled"; fillcolor="#eef6ea"; color="#88a97a";
   nginx[label="Servidor Web\\n(Nginx)\\nTLS, arquivos estáticos,\\nproxy reverso" fillcolor="#ffffff"];
   subgraph cluster_jvm {{ label="JVM"; style="rounded,filled"; fillcolor="#fbefe2"; color="#c79b6b";
     tomcat[label="Servidor de aplicação\\n(contêiner Servlet\\nTomcat)"]; appl[label="Aplicação\\n(Spring)"]; }}
   pg[label="SGBD\\n(PostgreSQL)" shape=cylinder fillcolor="#f3e9f7"];
   sosrv[label="Sistema operacional Linux\\n(systemd, rede, processos, arquivos)" fillcolor="#e1eedb"]; }}
 usuario -> ui; ui -> render [style=invis]; ui -> js [style=invis]; ui -> rede [style=invis];
 rede -> socli [label="chamadas\\nde sistema"]; socli -> dns [label="DNS (53/UDP)"];
 socli -> nginx [label="HTTPS\\n(TCP 443)"]; nginx -> tomcat [label="HTTP\\n127.0.0.1:8080"]; tomcat -> appl [label="API\\nServlet"];
 appl -> pg [label="SQL via\\nJDBC (5432)"]; pg -> sosrv [style=invis];
}}""")

seq1 = sequence(
    [("u", "Usuário", "ator"), ("n", "Navegador", "cliente"), ("d", "DNS", "infra"),
     ("w", "Servidor Web\n(Nginx)", "infra"), ("a", "Servidor de\naplicação", "app"), ("b", "SGBD", "dados")],
    [("msg", "u", "n", "1. informa https://auth.example.com/", False),
     ("msg", "n", "d", "2. consulta registros A/AAAA", False),
     ("msg", "d", "n", "3. endereço IP + TTL", True),
     ("msg", "n", "w", "4. conexão TCP (SYN, SYN-ACK, ACK) porta 443", False),
     ("msg", "n", "w", "5. TLS 1.3: ClientHello (SNI, ALPN)", False),
     ("msg", "w", "n", "6. ServerHello, certificado, Finished", True),
     ("msg", "n", "w", "7. GET / (HTTP/2)", False),
     ("self", "w", "8. seleciona server/location; lê arquivo"),
     ("msg", "w", "n", "9. 200 OK text/html (+ CSS, JS)", True),
     ("self", "n", "10. constrói DOM/CSSOM e renderiza"),
     ("msg", "u", "n", "11. preenche credenciais e aciona Entrar", False),
     ("msg", "n", "w", "12. POST /api/v1/autenticacoes (JSON)", False),
     ("msg", "w", "a", "13. proxy_pass (HTTP/1.1 local)", False),
     ("self", "a", "14. thread do pool → filtros → servlet"),
     ("msg", "a", "b", "15. consulta SQL (JDBC)", False),
     ("msg", "b", "a", "16. linhas resultantes", True),
     ("msg", "a", "w", "17. 200 ou 401 (application/json)", True),
     ("msg", "w", "n", "18. resposta encaminhada + log de acesso", True),
     ("msg", "n", "u", "19. atualiza o DOM com o resultado", True)],
    width=720)
(OUT / "f2_fluxo_web.svg").write_text(seq1)

dot("f3_navegador", f"""
digraph G {{ rankdir=LR; graph[{F} fontsize=11 nodesep=0.3 ranksep=0.35];
 node[{F} fontsize=10 shape=box style="rounded,filled" fillcolor="#e8f0fb"]; edge[{F} fontsize=9];
 resp[label="Resposta HTTP\\n(bytes)" fillcolor="#ffffff"]; html[label="Analisador\\nHTML"]; dom[label="DOM"];
 css[label="Analisador\\nCSS"]; cssom[label="CSSOM"]; js[label="Motor JavaScript\\n+ laço de eventos" fillcolor="#fbefe2"];
 rt[label="Árvore de\\nrenderização"]; lay[label="Layout\\n(geometria)"]; pnt[label="Pintura"]; cmp[label="Composição\\n→ tela"];
 fetch[label="API Fetch\\n(requisições\\nassíncronas)" fillcolor="#fbefe2"];
 resp -> html -> dom; html -> css [label="<link>"]; css -> cssom; html -> js [label="<script>"];
 js -> dom [label="lê/altera"]; dom -> rt; cssom -> rt; rt -> lay -> pnt -> cmp; js -> fetch [label="fetch()"]; fetch -> js [label="Promise" style=dashed];
}}""")

dot("f4_servidor", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=11 nodesep=0.22 ranksep=0.3 compound=true];
 node[{F} fontsize=9.5 shape=box style="rounded,filled" fillcolor="#ffffff"]; edge[{F} fontsize=8.5];
 cli[label="Navegador" fillcolor="#e8f0fb"];
 subgraph cluster_ng {{ label="Nginx"; style="rounded,filled"; fillcolor="#eef6ea";
   master[label="Processo mestre\\n(lê nginx.conf,\\nabre portas)"]; worker[label="Processos\\ntrabalhadores\\n(laço de eventos\\nepoll)"];
   loc[label="Seleção de\\nserver / location"]; est[label="Arquivos\\nestáticos"]; prox[label="Módulo\\nproxy"]; }}
 subgraph cluster_tc {{ label="Tomcat + Spring (JVM)"; style="rounded,filled"; fillcolor="#fbefe2";
   con[label="Conector\\nHTTP (NIO)"]; pool[label="Pool de\\nthreads"]; fil[label="Cadeia de\\nfiltros"]; disp[label="Dispatcher\\nServlet"];
   ctrl[label="Controlador\\n→ serviço"]; conv[label="Conversor\\nJSON"]; hik[label="Pool de\\nconexões\\nJDBC"]; }}
 subgraph cluster_pg {{ label="PostgreSQL"; style="rounded,filled"; fillcolor="#f3e9f7";
   post[label="postmaster"]; back[label="Processo\\nbackend\\n(parse, plano,\\nexecução)"]; }}
 cli -> worker [label="HTTPS"]; master -> worker [label="fork" style=dashed]; worker -> loc; loc -> est [label="/"]; loc -> prox [label="/api/"];
 prox -> con [label="HTTP"]; con -> pool -> fil -> disp -> ctrl; ctrl -> conv [label="objeto"]; ctrl -> hik [label="SQL"];
 hik -> back [label="protocolo\\nPostgreSQL"]; post -> back [label="fork" style=dashed];
}}""")

# ---------------------------------------------------------------- Seção 2
dot("f5_contexto", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=11 nodesep=0.6 ranksep=0.6];
 node[{F} fontsize=10 shape=box style="rounded,filled"]; edge[{F} fontsize=9];
 u[label="Usuário\\n[Pessoa]\\n\\nTitular de uma conta\\nque deseja provar\\nsua identidade" fillcolor="#08427b" fontcolor="white"];
 s[label="Sistema Web de Autenticação\\n[Sistema de software]\\n\\nRecebe credenciais, verifica-as\\ne retorna a identidade do usuário" fillcolor="#1168bd" fontcolor="white" width=2.8];
 c[label="Fluxo cliente subsequente\\n[Sistema externo]\\n\\nUsa a identidade retornada\\npara continuar o fluxo\\n(fora do escopo)" fillcolor="#999999" fontcolor="white"];
 p[label="Processo de cadastro\\nde usuários\\n[Sistema externo]\\n\\nPopula o repositório\\n(fora do escopo)" fillcolor="#999999" fontcolor="white"];
 u -> s [label="Envia identificador\\ne senha\\n[HTTPS]"]; s -> c [label="Identidade do usuário\\n[JSON]" style=dashed];
 p -> s [label="Usuários e hashes\\nde senha [SQL]" style=dashed];
}}""")

dot("f6_conteineres", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=11 nodesep=0.4 ranksep=0.6];
 node[{F} fontsize=9.5 shape=box style="rounded,filled" fontcolor="white" fillcolor="#438dd5"]; edge[{F} fontsize=8.5];
 u[label="Usuário\\n[Pessoa]" fillcolor="#08427b"];
 subgraph cluster_s {{ label="Sistema Web de Autenticação"; style="dashed"; fontcolor="#333333"; color="#666666";
   spa[label="Página de login\\n[Contêiner: HTML, CSS,\\nJavaScript no navegador]\\n\\nColeta credenciais e\\napresenta o resultado"];
   web[label="Servidor Web\\n[Contêiner: Nginx]\\n\\nTermina TLS, entrega\\narquivos estáticos,\\nlimita taxa e encaminha\\n/api/ à API"];
   api[label="API de Autenticação\\n[Contêiner: Java, Spring,\\nTomcat embutido]\\n\\nVerifica credenciais e\\nretorna a identidade"];
   db[label="Repositório de Usuários\\n[Contêiner: PostgreSQL]\\n\\nTabela usuario com\\nhash Argon2id da senha" shape=cylinder fillcolor="#438dd5"]; }}
 u -> spa [label="Usa\\n[HTTPS]" fontcolor="#333333"]; spa -> web [label="GET estáticos;\\nPOST /api/v1/autenticacoes\\n[HTTPS/JSON]"];
 web -> api [label="Encaminha\\n[HTTP local]"]; api -> db [label="Lê usuário\\n[SQL/JDBC]"];
}}""")

dot("f7_componentes", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=10.5 nodesep=0.35 ranksep=0.45 newrank=true];
 node[{F} fontsize=9.5 shape=component style="filled" fillcolor="#ffffff"]; edge[{F} fontsize=8.5];
 subgraph cluster_cli {{ label="Camada de apresentação (executa no navegador)"; style="rounded,filled"; fillcolor="#e8f0fb";
   pag[label="PaginaLogin\\n(index.html, login.css)"]; ctl[label="ControladorLogin\\n(login.js)"]; cliapi[label="ClienteApiAutenticacao\\n(api.js)"]; }}
 subgraph cluster_api {{ label="Camada de interface da API — adaptadores de entrada (servidor de aplicação)"; style="rounded,filled"; fillcolor="#fbefe2";
   rc[label="AutenticacaoController"]; me[label="ManipuladorErrosApi"]; dto[label="DTOs: SolicitacaoAutenticacao,\\nIdentidadeUsuarioResposta"]; }}
 subgraph cluster_app {{ label="Camada de aplicação e domínio — núcleo independente de tecnologia"; style="rounded,filled"; fillcolor="#fff7d6";
   svc[label="ServicoAutenticacao"]; dom[label="Domínio: Credenciais, Usuario,\\nIdentidadeUsuario, FalhaAutenticacao"];
   prt[label="Portas (interfaces): RepositorioUsuarios,\\nVerificadorSenha, RegistradorEventos" shape=box style="rounded,dashed,filled"]; }}
 subgraph cluster_inf {{ label="Camada de infraestrutura — adaptadores de saída"; style="rounded,filled"; fillcolor="#eef6ea";
   rep[label="RepositorioUsuariosJdbc"]; ver[label="VerificadorSenhaArgon2id"]; reg[label="RegistradorEventosLog"]; }}
 {{rank=same; pag; ctl; cliapi;}} {{rank=same; me; rc; dto;}} {{rank=same; dom; svc;}} {{rank=same; rep; ver; reg;}}
 pag -> ctl [label="eventos"]; ctl -> cliapi; cliapi -> rc [label="POST JSON\\n(via Nginx)"];
 rc -> dto [style=dashed label="usa"]; me -> rc [label="trata exceções" style=dashed]; rc -> svc [label="autenticar()"];
 svc -> dom [style=dashed label="usa"]; svc -> prt [label="depende de"];
 prt -> ver [label="implementada por" style=dashed arrowtail=empty dir=back]; prt -> rep [style=dashed arrowtail=empty dir=back]; prt -> reg [style=dashed arrowtail=empty dir=back];
}}""")

dot("f8_dados", f"""
digraph G {{ graph[{F}]; node[{F} shape=plaintext fontsize=10];
 t[label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="4" bgcolor="#ffffff">
 <tr><td bgcolor="#f3e9f7" colspan="3"><b>usuario</b></td></tr>
 <tr><td align="left"><b>PK</b></td><td align="left">id</td><td align="left">UUID NOT NULL</td></tr>
 <tr><td align="left"><b>UK</b></td><td align="left">login</td><td align="left">VARCHAR(64) NOT NULL</td></tr>
 <tr><td align="left"><b>UK</b></td><td align="left">email</td><td align="left">VARCHAR(254) NOT NULL</td></tr>
 <tr><td align="left"></td><td align="left">nome_exibicao</td><td align="left">VARCHAR(120) NOT NULL</td></tr>
 <tr><td align="left"></td><td align="left">hash_senha</td><td align="left">VARCHAR(255) NOT NULL</td></tr>
 <tr><td align="left"></td><td align="left">criado_em</td><td align="left">TIMESTAMPTZ NOT NULL</td></tr>
 <tr><td align="left"></td><td align="left">atualizado_em</td><td align="left">TIMESTAMPTZ NOT NULL</td></tr>
 </table>>];
}}""")


def cls(name, attrs, ops, stereo=None, fill="#ffffff"):
    st = f'<tr><td><i>«{stereo}»</i></td></tr>' if stereo else ""
    a = "<br align='left'/>".join(attrs) + "<br align='left'/>" if attrs else " "
    o = "<br align='left'/>".join(ops) + "<br align='left'/>" if ops else " "
    return (f'<<table border="1" cellborder="1" cellspacing="0" cellpadding="3" bgcolor="{fill}">{st}'
            f'<tr><td><b>{name}</b></td></tr><tr><td align="left" balign="left">{a}</td></tr>'
            f'<tr><td align="left" balign="left">{o}</td></tr></table>>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


C = {
 "ctrl": cls("AutenticacaoController", [], ["+ autenticar(req): ResponseEntity"], "RestController", "#fbefe2"),
 "me": cls("ManipuladorErrosApi", [], ["+ tratarFalha(e): ProblemDetail", "+ tratarValidacao(e): ProblemDetail", "+ tratarInesperado(e): ProblemDetail"], "RestControllerAdvice", "#fbefe2"),
 "req": cls("SolicitacaoAutenticacao", ["identificador: String", "senha: String"], ["+ toString(): String"], "record", "#fbefe2"),
 "resp": cls("IdentidadeUsuarioResposta", ["id: UUID", "login: String", "email: String", "nomeExibicao: String", "autenticadoEm: Instant"], ["+ de(i): IdentidadeUsuarioResposta"], "record", "#fbefe2"),
 "svc": cls("ServicoAutenticacao", ["- repositorio", "- verificador", "- registrador", "- relogio: Clock"], ["+ autenticar(c): IdentidadeUsuario"], "Service", "#fff7d6"),
 "cred": cls("Credenciais", ["- identificador: String", "- senha: char[]"], ["+ de(id, senha): Credenciais", "+ descartarSenha(): void"], "valor", "#fff7d6"),
 "usr": cls("Usuario", ["- id: UUID", "- login: String", "- email: String", "- nomeExibicao: String", "- hashSenha: String"], ["+ paraIdentidade(t): IdentidadeUsuario"], "entidade", "#fff7d6"),
 "idt": cls("IdentidadeUsuario", ["- id: UUID", "- login: String", "- email: String", "- nomeExibicao: String", "- autenticadoEm: Instant"], [" "], "valor", "#fff7d6"),
 "exc": cls("FalhaAutenticacaoException", ["- motivoInterno: MotivoFalha"], ["+ getMessage(): String"], "exceção", "#fff7d6"),
 "rep": cls("RepositorioUsuarios", [" "], [esc("+ buscarPorIdentificador(id): Optional<Usuario>")], "interface", "#fff7d6"),
 "ver": cls("VerificadorSenha", [" "], ["+ verificar(senha, hash): boolean", "+ hashFicticio(): String"], "interface", "#fff7d6"),
 "reg": cls("RegistradorEventos", [" "], ["+ sucesso(idMascarado, usuarioId)", "+ falha(idMascarado, motivo)"], "interface", "#fff7d6"),
 "repj": cls("RepositorioUsuariosJdbc", ["- jdbc: JdbcClient"], [esc("+ buscarPorIdentificador(id): Optional<Usuario>")], "Repository", "#eef6ea"),
 "vera": cls("VerificadorSenhaArgon2id", ["- codificador: Argon2PasswordEncoder", "- hashFicticio: String", "- permissoes: Semaphore"], ["+ verificar(senha, hash): boolean", "+ hashFicticio(): String"], "Component", "#eef6ea"),
 "regl": cls("RegistradorEventosLog", ["- log: Logger"], ["+ sucesso(idMascarado, usuarioId)", "+ falha(idMascarado, motivo)"], "Component", "#eef6ea"),
}
def classes(nome, chaves, linhas, arestas):
    nodes = "\n".join(f" {k}[label={C[k]}];" for k in chaves)
    ranks = " ".join("{{rank=same; " + "; ".join(r) + ";}}" for r in linhas)
    dot(nome, f"""digraph G {{{{ rankdir=TB; graph[{F} nodesep=0.35 ranksep=0.45]; node[{F} shape=plaintext fontsize=10]; edge[{F} fontsize=8.5 arrowsize=0.7];
{nodes}
{ranks}
{arestas} }}}}""")


classes("f9a_classes_api", ["ctrl", "me", "req", "resp", "svc", "exc", "cred", "idt"],
        [["ctrl", "me"], ["req", "resp"], ["svc", "exc"], ["cred", "idt"]],
        """ ctrl -> req [style=dashed label="«recebe»"]; ctrl -> resp [style=dashed label="«produz»"]; me -> exc [style=dashed label="«trata»"];
 req -> svc [style=invis]; ctrl -> svc [label="usa"]; svc -> exc [style=dashed label="«lança»"]; svc -> cred [style=dashed label="«usa»"]; svc -> idt [style=dashed label="«retorna»"];
 resp -> idt [style=dashed dir=back label="«converte»"];""")

C["svc2"] = cls("ServicoAutenticacao", [" "], ["+ autenticar(c): IdentidadeUsuario"], "Service", "#fff7d6")
classes("f9b_classes_nucleo", ["svc2", "usr", "rep", "ver", "reg", "repj", "vera", "regl"],
        [["svc2", "usr"], ["rep", "ver", "reg"], ["repj", "vera", "regl"]],
        """ svc2 -> rep; svc2 -> ver; svc2 -> reg; rep -> usr [style=dashed label="«retorna»" constraint=false];
 rep -> repj [style=dashed dir=back arrowtail=empty]; ver -> vera [style=dashed dir=back arrowtail=empty]; reg -> regl [style=dashed dir=back arrowtail=empty];""")

seq2 = sequence(
    [("c", "ControladorLogin\n(navegador)", "cliente"), ("w", "Nginx", "infra"), ("r", "Autenticacao\nController", "app"),
     ("s", "Servico\nAutenticacao", "app"), ("p", "Repositorio\nUsuariosJdbc", "dados"), ("v", "Verificador\nSenhaArgon2id", "app"), ("g", "Registrador\nEventosLog", "app")],
    [("msg", "c", "w", "POST /api/v1/autenticacoes", False),
     ("msg", "w", "r", "encaminha (limite de taxa ok)", False),
     ("self", "r", "valida DTO (Bean Validation)"),
     ("msg", "r", "s", "autenticar(credenciais)", False),
     ("self", "s", "normaliza identificador e senha"),
     ("msg", "s", "p", "buscarPorIdentificador(id)", False),
     ("msg", "p", "s", "Optional<Usuario>", True),
     ("msg", "s", "v", "verificar(senha, hash real ou fictício)", False),
     ("msg", "v", "s", "boolean confere", True),
     ("self", "s", "descarta senha da memória"),
     ("frame", "alt", "usuário existe e confere"),
     ("msg", "s", "g", "sucesso(idMascarado, usuarioId)", False),
     ("msg", "s", "r", "IdentidadeUsuario", True),
     ("msg", "r", "w", "200 OK + IdentidadeUsuarioResposta", True),
     ("else", "senão (inexistente ou senha incorreta)"),
     ("msg", "s", "g", "falha(idMascarado, motivo)", False),
     ("msg", "s", "r", "lança FalhaAutenticacaoException", True),
     ("msg", "r", "w", "401 problem+json (via ManipuladorErrosApi)", True),
     ("endframe",),
     ("msg", "w", "c", "resposta HTTPS", True)],
    width=740)
(OUT / "f10_seq_autenticacao.svg").write_text(seq2)

dot("f11_atividade", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=10 nodesep=0.3 ranksep=0.25]; node[{F} fontsize=9.5 shape=box style="rounded,filled" fillcolor="#ffffff"]; edge[{F} fontsize=8.5];
 ini[shape=circle label="" width=0.2 style=filled fillcolor=black];
 a1[label="Receber requisição POST"]; d1[shape=diamond label="Formato\\nválido?" fillcolor="#fff7d6"];
 e400[label="Retornar 400\\n(problem+json)" fillcolor="#fde2e2"];
 a2[label="Normalizar identificador (trim, minúsculas)\\ne senha (Unicode NFKC)"]; a3[label="Buscar usuário por login ou e-mail"];
 d2[shape=diamond label="Usuário\\nexiste?" fillcolor="#fff7d6"]; a4[label="hash ← hash armazenado"]; a5[label="hash ← hash fictício"];
 a6[label="confere ← Argon2id.verificar(senha, hash)"]; a7[label="Descartar senha da memória"];
 d3[shape=diamond label="Existe\\nE confere?" fillcolor="#fff7d6"];
 ok[label="Registrar sucesso;\\nretornar 200 + identidade" fillcolor="#e1f3dc"]; nok[label="Registrar falha;\\nretornar 401 genérico" fillcolor="#fde2e2"];
 fim[shape=doublecircle label="" width=0.15 style=filled fillcolor=black];
 ini -> a1 -> d1; d1 -> e400 [label="não"]; d1 -> a2 [label="sim"]; a2 -> a3 -> d2; d2 -> a4 [label="sim"]; d2 -> a5 [label="não"];
 a4 -> a6; a5 -> a6; a6 -> a7 -> d3; d3 -> ok [label="sim"]; d3 -> nok [label="não"]; ok -> fim; nok -> fim; e400 -> fim;
}}""")

dot("f12_implantacao", f"""
digraph G {{ rankdir=TB; graph[{F} fontsize=10 nodesep=0.3 ranksep=0.5]; node[{F} fontsize=9.5 shape=box3d style=filled fillcolor="#ffffff"]; edge[{F} fontsize=8.5];
 subgraph cluster_u {{ label="«dispositivo» Estação do usuário"; style=filled; fillcolor="#e8f0fb";
   b[label="«ambiente de execução»\\nNavegador\\n─────────\\nindex.html, login.css,\\nlogin.js, api.js"]; }}
 subgraph cluster_app {{ label="«nó» Servidor de aplicação (Linux) — rede DMZ"; style=filled; fillcolor="#eef6ea";
   n[label="«serviço systemd» nginx\\n─────────\\n:80 → redireciona\\n:443 TLS 1.2/1.3\\n/var/www/autenticacao"];
   j[label="«serviço systemd» autenticacao\\n─────────\\nJVM: autenticacao.jar\\n(Spring Boot + Tomcat)\\n127.0.0.1:8080"]; }}
 subgraph cluster_db {{ label="«nó» Servidor de banco de dados (Linux) — rede privada"; style=filled; fillcolor="#f3e9f7";
   p[label="«serviço systemd» postgresql\\n─────────\\n:5432 (aceita só a\\nrede privada)\\nbanco autenticacao"]; }}
 b -> n [label="HTTPS 443"]; n -> j [label="HTTP loopback"]; j -> p [label="JDBC/TLS 5432\\npapel somente leitura"];
}}""")

print("figuras geradas em", OUT)
