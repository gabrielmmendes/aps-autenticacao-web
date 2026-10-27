# APS – Software Web para Autenticação de Usuários

Domínios de Software – 2026/2 – UFG/INF. Autoria: Gabriel Matos Mendes; Kezer dos Santos Souza.

## Gerar o PDF

```bash
pip install weasyprint      # requer também Graphviz (comando `dot`)
python3 diagramas/gerar.py  # gera as figuras em build/fig
python3 build.py            # gera build/APS_Autenticacao_Web.pdf
```

## Onde editar

- `conteudo.html` – texto de todos os itens de informação (macros `[[c:chave]]`, `[[fig:id]]`, `[[tab:id]]`, `[[sec:X.Y]]`).
- `build.py` – autoria/revisão de cada item (`ITENS`), referências (`REFS`) e URL do repositório (`REPOSITORIO`).
- `registros_comunicacao.csv` – registros reais de comunicação e reuniões (Apêndice A).
- `diagramas/gerar.py` – fontes das figuras.

## Fluxo de trabalho

Uma issue por item no quadro Kanban (A fazer → Em autoria → Em revisão → Concluído); um ramo por item
(`item/2.5-api`); pull request revisado e aprovado pelo revisor indicado em `ITENS`.
