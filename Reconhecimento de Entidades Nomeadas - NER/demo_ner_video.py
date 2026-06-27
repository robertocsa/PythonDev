"""
Demonstração de NER (Reconhecimento de Entidades Nomeadas) em português,
pensada para ser GRAVADA NA TELA e usada no vídeo explicativo do canal.

O QUE ESTE SCRIPT FAZ (nessa ordem, com pausas pensadas para a gravação):
  1. Mostra o texto de entrada (um "contrato" fictício, mas realista).
  2. Carrega o modelo de PLN em português.
  3. Roda o NER estatístico (spaCy) E complementa com regras/regex
     para DATA e VALOR — a abordagem híbrida explicada no Bloco 5 do roteiro.
  4. Revela as entidades encontradas, uma a uma, numa tabela colorida no terminal.
  5. Mostra um resumo final com contagem por categoria.
  6. Gera uma página HTML com o texto original e caixas coloridas sobre
     cada entidade — a MESMA estética pedida no gancho do vídeo (Bloco 1),
     só que com texto real sendo processado de verdade, não gerado por IA.

INSTALAÇÃO:
    pip install spacy rich
    python -m spacy download pt_core_news_lg

EXECUÇÃO:
    python demo_ner_video.py

GRAVAÇÃO DE TELA (sugestão gratuita):
    OBS Studio (open-source, multiplataforma) é a opção mais robusta e
    gratuita para capturar o terminal e a janela do navegador que abre
    com a visualização HTML no passo 6.
"""

import re
import time
import webbrowser
from collections import Counter
from pathlib import Path

import spacy
from spacy import displacy
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO — ajuste aqui o ritmo da gravação
# ---------------------------------------------------------------------------
VELOCIDADE = 1.0  # aumente para deixar as pausas mais longas (ex: 1.5), reduza para acelerar (ex: 0.5)

console = Console()

# ---------------------------------------------------------------------------
# TEXTO DE EXEMPLO — um "contrato" fictício com pessoas, organizações,
# locais, datas e valores, no mesmo espírito do gancho do vídeo
# ---------------------------------------------------------------------------
TEXTO_EXEMPLO = """
No dia 15 de março de 2024, a empresa Construtora Horizonte Ltda., com sede
em São Paulo, firmou um contrato de prestação de serviços com o cliente
Carlos Eduardo Mendes, no valor total de R$ 350.000,00, a ser pago em três
parcelas. A primeira parcela, de R$ 120.000,00, foi quitada em 20 de março
de 2024, conforme comprovante emitido pelo Banco Itaú.

Em 02 de abril de 2024, a Construtora Horizonte Ltda. iniciou as obras no
terreno localizado em Campinas, sob supervisão da engenheira Fernanda
Albuquerque. O projeto também contou com a parceria da empresa Engenharia
Sólida S.A., responsável pelo fornecimento de materiais, em um contrato
adicional de R$ 80.000,00 assinado em 10 de abril de 2024.

A reunião de encerramento da primeira fase está prevista para 30 de junho
de 2024, na sede da empresa em São Paulo, com a presença de Carlos Eduardo
Mendes, Fernanda Albuquerque e o diretor financeiro Ricardo Tavares.
""".strip()

# ---------------------------------------------------------------------------
# Paleta de cores — a MESMA usada no código Manim, pra manter consistência
# visual entre todas as peças do vídeo
# ---------------------------------------------------------------------------
CORES_TERMINAL = {
    "PER": "bold blue",
    "ORG": "bold green",
    "LOC": "bold yellow1",
    "DATA": "bold orange3",
    "VALOR": "bold red",
    "MISC": "bold magenta",
}

CORES_HTML = {
    "PER": "#3B82F6",
    "ORG": "#22C55E",
    "LOC": "#FACC15",
    "DATA": "#F97316",
    "VALOR": "#EF4444",
    "MISC": "#A855F7",
}

NOMES_PT = {
    "PER": "PESSOA",
    "ORG": "ORGANIZAÇÃO",
    "LOC": "LOCAL",
    "DATA": "DATA",
    "VALOR": "VALOR",
    "MISC": "OUTRO",
}

# Regex complementares — cobrem datas e valores em R$ que o modelo
# estatístico sozinho normalmente não rotula com precisão
REGEX_DATA = re.compile(r"\d{1,2}\s+de\s+[a-zçãéê]+\s+de\s+\d{4}", re.IGNORECASE)
REGEX_VALOR = re.compile(r"R\$\s?[\d.]+,\d{2}")


def pausa(segundos):
    time.sleep(segundos * VELOCIDADE)


def mostrar_intro():
    console.clear()
    painel = Panel.fit(
        "[bold white]Extração de Entidades Nomeadas (NER)[/bold white]\n"
        "[dim]Identificando pessoas, organizações, locais, datas e valores em texto[/dim]",
        border_style="cyan",
    )
    console.print(painel)
    console.print()
    pausa(1.5)


def carregar_modelo():
    with console.status("[bold cyan]Carregando modelo de linguagem em português...", spinner="dots"):
        nlp = spacy.load("pt_core_news_lg")
        pausa(1.2)
    console.print("[bold green]✓ Modelo carregado com sucesso!\n")
    pausa(0.6)
    return nlp


def mostrar_texto_original(texto):
    console.print("[bold white]Texto de entrada:[/bold white]\n")
    console.print(Panel(texto, border_style="grey50"))
    console.print()
    pausa(2)


def adicionar_entidades_por_regex(doc):
    """
    Combina as entidades do modelo estatístico (spaCy) com entidades
    encontradas por regex (datas e valores monetários) — a abordagem
    híbrida explicada no Bloco 5 do roteiro: modelo + regras.
    """
    entidades = list(doc.ents)
    ocupados = [(ent.start_char, ent.end_char) for ent in entidades]

    def sobrepoe(inicio, fim):
        return any(not (fim <= o_ini or inicio >= o_fim) for o_ini, o_fim in ocupados)

    for padrao, rotulo in [(REGEX_DATA, "DATA"), (REGEX_VALOR, "VALOR")]:
        for match in padrao.finditer(doc.text):
            inicio, fim = match.span()
            if sobrepoe(inicio, fim):
                continue
            span = doc.char_span(inicio, fim, label=rotulo, alignment_mode="expand")
            if span is not None:
                entidades.append(span)
                ocupados.append((inicio, fim))

    doc.set_ents(sorted(entidades, key=lambda s: s.start_char))
    return doc


def revelar_entidades(doc):
    console.print("[bold white]Entidades detectadas (modelo + regras):[/bold white]\n")

    tabela = Table(show_header=True, header_style="bold white")
    tabela.add_column("Texto encontrado", style="white")
    tabela.add_column("Categoria", style="white")
    tabela.add_column("Origem", style="dim")

    with Live(tabela, console=console, refresh_per_second=4):
        for ent in doc.ents:
            cor = CORES_TERMINAL.get(ent.label_, "white")
            nome_pt = NOMES_PT.get(ent.label_, ent.label_)
            origem = "regex" if ent.label_ in ("DATA", "VALOR") else "modelo NER"
            tabela.add_row(
                f"[{cor}]{ent.text}[/{cor}]",
                f"[{cor}]{nome_pt}[/{cor}]",
                origem,
            )
            pausa(0.55)

    console.print()
    pausa(1)


def mostrar_resumo(doc):
    contagem = Counter(ent.label_ for ent in doc.ents)

    console.print("[bold white]Resumo por categoria:[/bold white]\n")
    tabela = Table(show_header=False, box=None)
    tabela.add_column("Categoria")
    tabela.add_column("Qtd", justify="right")
    tabela.add_column("Barra")

    for label, qtd in contagem.most_common():
        cor = CORES_TERMINAL.get(label, "white")
        nome_pt = NOMES_PT.get(label, label)
        barra = "█" * qtd
        tabela.add_row(f"[{cor}]{nome_pt}[/{cor}]", str(qtd), f"[{cor}]{barra}[/{cor}]")

    console.print(tabela)
    console.print()
    pausa(2)


def gerar_visualizacao_html(doc, caminho_saida="ner_visualizacao.html"):
    """
    Gera uma página HTML com o texto original e caixas coloridas sobre
    cada entidade — útil pra gravar diretamente no navegador e usar
    como o efeito visual do gancho (Bloco 1), só que com dados reais.
    """
    html = displacy.render(doc, style="ent", page=True, options={"colors": CORES_HTML})
    caminho = Path(caminho_saida)
    caminho.write_text(html, encoding="utf-8")
    console.print(f"[bold green]✓ Visualização salva em:[/bold green] {caminho.resolve()}")
    webbrowser.open(caminho.resolve().as_uri())


def main():
    mostrar_intro()
    nlp = carregar_modelo()
    mostrar_texto_original(TEXTO_EXEMPLO)

    with console.status("[bold cyan]Analisando texto e extraindo entidades...", spinner="dots"):
        doc = nlp(TEXTO_EXEMPLO)
        doc = adicionar_entidades_por_regex(doc)
        pausa(1.2)

    revelar_entidades(doc)
    mostrar_resumo(doc)
    gerar_visualizacao_html(doc)

    console.print("\n[bold cyan]Fim da demonstração.[/bold cyan]")


if __name__ == "__main__":
    main()
