#!/usr/bin/env python3
"""
Gerador de Relatório PDF Corporativo para Análise COCOMO II
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io


# Cores corporativas modernas
COLORS = {
    'primary': colors.HexColor('#1E3A8A'),      # Azul escuro
    'secondary': colors.HexColor('#3B82F6'),    # Azul médio
    'accent': colors.HexColor('#60A5FA'),       # Azul claro
    'success': colors.HexColor('#10B981'),      # Verde
    'warning': colors.HexColor('#F59E0B'),      # Laranja
    'danger': colors.HexColor('#EF4444'),       # Vermelho
    'text': colors.HexColor('#1F2937'),         # Cinza escuro
    'light': colors.HexColor('#F3F4F6'),        # Cinza claro
    'white': colors.white,
}


class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado com cabeçalho e rodapé"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        """Desenha cabeçalho e rodapé"""
        page_num = len(self._saved_page_states)

        # Linha superior decorativa
        self.setStrokeColor(COLORS['primary'])
        self.setLineWidth(3)
        self.line(50, A4[1] - 50, A4[0] - 50, A4[1] - 50)

        # Rodapé
        self.setFont('Helvetica', 8)
        self.setFillColor(COLORS['text'])

        # Data de geração
        footer_text = f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        self.drawString(50, 30, footer_text)

        # Número da página
        page_text = f"Página {page_num} de {page_count}"
        self.drawRightString(A4[0] - 50, 30, page_text)

        # Linha inferior decorativa
        self.setStrokeColor(COLORS['primary'])
        self.setLineWidth(1)
        self.line(50, 40, A4[0] - 50, 40)


def create_matplotlib_chart(data, chart_type='bar', title='', labels=None, values=None):
    """Cria gráficos usando matplotlib"""
    fig, ax = plt.subplots(figsize=(6, 4))

    if chart_type == 'bar':
        bars = ax.bar(labels, values, color='#3B82F6', edgecolor='#1E3A8A', linewidth=1.5)
        ax.set_ylabel('Valor')

        # Adiciona valores sobre as barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)

    elif chart_type == 'pie':
        colors_pie = ['#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE']
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                           colors=colors_pie, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')

    ax.set_title(title, fontsize=12, fontweight='bold', color='#1E3A8A')
    plt.tight_layout()

    # Salva em buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()

    return img_buffer


def format_number(value, decimals=2):
    """Formata números com separadores de milhares"""
    if isinstance(value, (int, float)):
        if decimals == 0:
            return f"{value:,.0f}".replace(',', '.')
        return f"{value:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return str(value)


def create_info_table(data, title):
    """Cria tabela formatada para informações"""
    table_data = [[Paragraph(f"<b>{title}</b>",
                            ParagraphStyle('Title', fontSize=12, textColor=COLORS['primary']))]]

    for key, value in data:
        table_data.append([
            Paragraph(f"<b>{key}</b>", ParagraphStyle('Key', fontSize=10, textColor=COLORS['text'])),
            Paragraph(str(value), ParagraphStyle('Value', fontSize=10, textColor=COLORS['text']))
        ])

    table = Table(table_data, colWidths=[7*cm, 9*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),

        ('BACKGROUND', (0, 1), (-1, -1), COLORS['white']),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['primary']),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], COLORS['light']]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 1), (-1, -1), 10),
        ('RIGHTPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    return table


def create_metric_box(title, value, subtitle='', color=COLORS['primary']):
    """Cria caixa de métrica destacada"""
    data = [[
        Paragraph(f"<b>{title}</b>",
                 ParagraphStyle('BoxTitle', fontSize=10, textColor=COLORS['white'], alignment=TA_CENTER)),
    ], [
        Paragraph(f"<b><font size=16>{value}</font></b>",
                 ParagraphStyle('BoxValue', fontSize=16, textColor=COLORS['white'], alignment=TA_CENTER)),
    ]]

    if subtitle:
        data.append([
            Paragraph(f"<i>{subtitle}</i>",
                     ParagraphStyle('BoxSubtitle', fontSize=8, textColor=COLORS['white'], alignment=TA_CENTER))
        ])

    table = Table(data, colWidths=[4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))

    return table


def format_ai_insights_for_pdf(insights_data, body_style):
    """Formata os insights de IA para inclusão no PDF

    Args:
        insights_data: Dict com os insights estruturados da IA
        body_style: Estilo de parágrafo para o corpo do texto

    Returns:
        Lista de elementos para adicionar ao PDF
    """
    elements = []

    if not insights_data or not isinstance(insights_data, dict):
        return elements

    # Valor do Código
    if "valor_codigo" in insights_data:
        vc = insights_data["valor_codigo"]

        if "avaliacao_geral" in vc:
            elements.append(Paragraph("<b>Avaliação Geral:</b>", body_style))
            elements.append(Paragraph(vc["avaliacao_geral"], body_style))
            elements.append(Spacer(1, 0.3*cm))

        if "pontos_fortes" in vc and vc["pontos_fortes"]:
            elements.append(Paragraph("<b>Pontos Fortes:</b>", body_style))
            for ponto in vc["pontos_fortes"]:
                elements.append(Paragraph(f"• {ponto}", body_style))
            elements.append(Spacer(1, 0.3*cm))

        if "areas_melhoria" in vc and vc["areas_melhoria"]:
            elements.append(Paragraph("<b>Áreas de Melhoria:</b>", body_style))
            for area in vc["areas_melhoria"]:
                elements.append(Paragraph(f"• {area}", body_style))
            elements.append(Spacer(1, 0.3*cm))

        if "valor_mercado_estimado" in vc:
            elements.append(Paragraph(f"<b>Valor de Mercado Estimado:</b> {vc['valor_mercado_estimado']}", body_style))
            elements.append(Spacer(1, 0.5*cm))

    # Métricas de Mercado
    if "metricas_mercado" in insights_data:
        mm = insights_data["metricas_mercado"]

        elements.append(Paragraph("<b>MÉTRICAS DE MERCADO</b>",
                                 ParagraphStyle('SubHeading', fontSize=12, textColor=COLORS['primary'], spaceAfter=10)))

        for key, label in [
            ("comparacao_industria", "Comparação com a Indústria"),
            ("maturidade_projeto", "Maturidade do Projeto"),
            ("qualidade_codigo", "Qualidade do Código"),
            ("velocidade_desenvolvimento", "Velocidade de Desenvolvimento"),
            ("custo_beneficio", "Análise de Custo-Benefício")
        ]:
            if key in mm:
                elements.append(Paragraph(f"<b>{label}:</b>", body_style))
                elements.append(Paragraph(mm[key], body_style))
                elements.append(Spacer(1, 0.2*cm))

        elements.append(Spacer(1, 0.3*cm))

    # Indicadores Chave
    if "indicadores_chave" in insights_data:
        ik = insights_data["indicadores_chave"]

        elements.append(Paragraph("<b>INDICADORES CHAVE</b>",
                                 ParagraphStyle('SubHeading', fontSize=12, textColor=COLORS['primary'], spaceAfter=10)))

        indicators_data = []
        for key, label in [
            ("roi_estimado", "ROI Estimado"),
            ("time_to_market", "Time to Market"),
            ("risco_tecnico", "Risco Técnico"),
            ("escalabilidade", "Escalabilidade"),
            ("sustentabilidade", "Sustentabilidade")
        ]:
            if key in ik:
                indicators_data.append([label, ik[key]])

        if indicators_data:
            indicators_table = Table(indicators_data, colWidths=[6*cm, 10*cm])
            indicators_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['light']),
                ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, COLORS['primary']),
            ]))
            elements.append(indicators_table)
            elements.append(Spacer(1, 0.5*cm))

    # Recomendações Estratégicas
    if "recomendacoes_estrategicas" in insights_data:
        re = insights_data["recomendacoes_estrategicas"]

        elements.append(Paragraph("<b>RECOMENDAÇÕES ESTRATÉGICAS</b>",
                                 ParagraphStyle('SubHeading', fontSize=12, textColor=COLORS['primary'], spaceAfter=10)))

        for periodo, titulo in [
            ("curto_prazo", "Curto Prazo (1-3 meses)"),
            ("medio_prazo", "Médio Prazo (3-6 meses)"),
            ("longo_prazo", "Longo Prazo (6+ meses)")
        ]:
            if periodo in re and re[periodo]:
                elements.append(Paragraph(f"<b>{titulo}:</b>", body_style))
                for rec in re[periodo]:
                    elements.append(Paragraph(f"• {rec}", body_style))
                elements.append(Spacer(1, 0.2*cm))

        elements.append(Spacer(1, 0.3*cm))

    # Oportunidades
    if "oportunidades" in insights_data:
        op = insights_data["oportunidades"]

        elements.append(Paragraph("<b>OPORTUNIDADES</b>",
                                 ParagraphStyle('SubHeading', fontSize=12, textColor=COLORS['primary'], spaceAfter=10)))

        for tipo, titulo in [
            ("monetizacao", "Monetização"),
            ("expansao", "Expansão"),
            ("otimizacao", "Otimização")
        ]:
            if tipo in op and op[tipo]:
                elements.append(Paragraph(f"<b>{titulo}:</b>", body_style))
                for oport in op[tipo]:
                    elements.append(Paragraph(f"• {oport}", body_style))
                elements.append(Spacer(1, 0.2*cm))

    return elements


def generate_pdf_report(json_file_path, output_pdf_path=None, include_ai_insights=True):
    """Gera relatório PDF a partir do arquivo JSON

    Args:
        json_file_path: Caminho para o arquivo JSON com os dados
        output_pdf_path: Caminho de saída do PDF (opcional)
        include_ai_insights: Se True, tenta gerar insights de IA (padrão: True)
    """

    # Carrega dados JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Define valores padrão para compatibilidade com JSONs antigos
    if 'project_name' not in data:
        data['project_name'] = 'Projeto'
    if 'project_path' not in data:
        data['project_path'] = str(Path(json_file_path).parent)
    if 'analysis_type' not in data:
        data['analysis_type'] = 'integrated'

    # Define nome do arquivo de saída
    if output_pdf_path is None:
        json_path = Path(json_file_path)
        output_pdf_path = json_path.parent / f"{json_path.stem}_relatorio.pdf"

    # Cria documento PDF
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=70,
        bottomMargin=50
    )

    # Estilos
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLORS['primary'],
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLORS['primary'],
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=COLORS['primary'],
        borderWidth=0,
        borderPadding=5,
        leftIndent=0
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=COLORS['text'],
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=14
    )

    # Elementos do PDF
    elements = []

    # ========== CAPA ==========
    elements.append(Spacer(1, 2*cm))

    elements.append(Paragraph(
        f"<b>RELATÓRIO DE ANÁLISE</b><br/><b>COCOMO II</b>",
        title_style
    ))
    elements.append(Spacer(1, 1*cm))

    # Caixa com nome do projeto
    project_box = Table([[
        Paragraph(f"<b>Projeto: {data['project_name']}</b>",
                 ParagraphStyle('ProjectName', fontSize=16, textColor=COLORS['white'], alignment=TA_CENTER))
    ]], colWidths=[14*cm])
    project_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['secondary']),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    elements.append(project_box)
    elements.append(Spacer(1, 2*cm))

    # Informações gerais
    gen_date = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))
    info_data = [
        ['Tipo de Análise', data['analysis_type'].upper()],
        ['Caminho do Projeto', data['project_path']],
        ['Data de Geração', gen_date.strftime('%d/%m/%Y %H:%M:%S')],
    ]

    info_table = Table(info_data, colWidths=[6*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['primary']),
    ]))
    elements.append(info_table)

    elements.append(PageBreak())

    # ========== RESUMO EXECUTIVO ==========
    elements.append(Paragraph("<b>RESUMO EXECUTIVO</b>", heading_style))
    elements.append(Spacer(1, 0.5*cm))

    cocomo = data['cocomo']
    git = data['git']
    integrated = data['integrated']

    summary_text = f"""
    Este relatório apresenta uma análise completa do projeto <b>{data['project_name']}</b> utilizando
    a metodologia COCOMO II integrada com métricas de repositório Git. O projeto possui <b>{format_number(cocomo['kloc'], 3)} KLOC</b>
    (mil linhas de código) e apresenta complexidade <b>{cocomo['complexity_level']}</b>.
    <br/><br/>
    A estimativa de esforço é de <b>{format_number(cocomo['effort_person_months'], 2)} pessoa-meses</b>,
    com duração prevista de <b>{format_number(cocomo['time_months'], 2)} meses</b> e
    necessidade de <b>{format_number(cocomo['people_required'], 1)} desenvolvedores</b>.
    O custo estimado para o projeto é de <b>R$ {format_number(cocomo['cost_estimate_brl'], 2)}</b>.
    <br/><br/>
    O repositório Git contém <b>{git['total_commits']} commits</b> de <b>{git['total_authors']} autores</b>,
    com idade de <b>{git['repository_age_days']} dias</b>. O score de produtividade dos desenvolvedores
    é de <b>{format_number(integrated['developer_productivity_score'], 2)}</b>.
    """

    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.5*cm))

    # Métricas principais em destaque
    metrics_row = Table([[
        create_metric_box('KLOC', format_number(cocomo['kloc'], 1), 'Linhas de Código', COLORS['primary']),
        create_metric_box('Esforço', f"{format_number(cocomo['effort_person_months'], 1)}", 'pessoa-meses', COLORS['secondary']),
        create_metric_box('Duração', f"{format_number(cocomo['time_months'], 1)}", 'meses', COLORS['accent']),
        create_metric_box('Custo', f"R$ {format_number(cocomo['cost_estimate_brl']/1000, 1)}k", 'Reais', COLORS['success']),
    ]], colWidths=[4*cm, 4*cm, 4*cm, 4*cm])

    elements.append(metrics_row)
    elements.append(Spacer(1, 1*cm))

    # ========== ANÁLISE COCOMO II ==========
    elements.append(Paragraph("<b>ANÁLISE COCOMO II</b>", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    cocomo_data = [
        ['Linhas de Código (KLOC)', f"{format_number(cocomo['kloc'], 3)} KLOC"],
        ['Esforço', f"{format_number(cocomo['effort_person_months'], 2)} pessoa-meses"],
        ['Tempo de Desenvolvimento', f"{format_number(cocomo['time_months'], 2)} meses"],
        ['Pessoas Necessárias', f"{format_number(cocomo['people_required'], 2)} desenvolvedores"],
        ['Pessoas para Manutenção', f"{format_number(cocomo['maintenance_people'], 2)} desenvolvedores"],
        ['Pessoas para Expansão', f"{format_number(cocomo['expansion_people'], 2)} desenvolvedores"],
        ['Produtividade', f"{format_number(cocomo['productivity'], 2)} linhas/pessoa-mês"],
        ['Custo Estimado (BRL)', f"R$ {format_number(cocomo['cost_estimate_brl'], 2)}"],
        ['Nível de Complexidade', cocomo['complexity_level']],
    ]

    elements.append(create_info_table(cocomo_data, 'Métricas COCOMO II'))
    elements.append(Spacer(1, 0.5*cm))

    # Gráfico de distribuição de pessoas
    img_buffer = create_matplotlib_chart(
        None, 'bar',
        'Distribuição de Pessoas',
        ['Desenvolvimento', 'Manutenção', 'Expansão'],
        [cocomo['people_required'], cocomo['maintenance_people'], cocomo['expansion_people']]
    )
    elements.append(Image(img_buffer, width=14*cm, height=9*cm))

    elements.append(PageBreak())

    # ========== ANÁLISE GIT ==========
    elements.append(Paragraph("<b>ANÁLISE DO REPOSITÓRIO GIT</b>", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    first_commit = datetime.fromisoformat(git['first_commit_date'])
    last_commit = datetime.fromisoformat(git['last_commit_date'])

    git_data = [
        ['Total de Commits', format_number(git['total_commits'], 0)],
        ['Total de Autores', format_number(git['total_authors'], 0)],
        ['Total de Inserções', format_number(git['total_insertions'], 0)],
        ['Total de Deleções', format_number(git['total_deletions'], 0)],
        ['Média de Mudanças por Commit', format_number(git['avg_changes_per_commit'], 2)],
        ['Média de Arquivos por Commit', format_number(git['avg_files_per_commit'], 2)],
        ['Commits por Dia', format_number(git['commits_per_day'], 2)],
        ['Primeiro Commit', first_commit.strftime('%d/%m/%Y %H:%M')],
        ['Último Commit', last_commit.strftime('%d/%m/%Y %H:%M')],
        ['Idade do Repositório', f"{git['repository_age_days']} dias"],
    ]

    elements.append(create_info_table(git_data, 'Métricas Git'))
    elements.append(Spacer(1, 0.5*cm))

    # Distribuição de commits por autor
    if git['authors_commits']:
        authors = list(git['authors_commits'].keys())
        commits = list(git['authors_commits'].values())

        img_buffer = create_matplotlib_chart(
            None, 'pie',
            'Distribuição de Commits por Autor',
            authors,
            commits
        )
        elements.append(Image(img_buffer, width=12*cm, height=8*cm))

    elements.append(PageBreak())

    # ========== ANÁLISE INTEGRADA ==========
    elements.append(Paragraph("<b>ANÁLISE INTEGRADA</b>", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    integrated_data = [
        ['KLOC (COCOMO)', f"{format_number(integrated['cocomo_kloc'], 3)} KLOC"],
        ['Esforço (COCOMO)', f"{format_number(integrated['cocomo_effort'], 2)} pessoa-meses"],
        ['Commits por Mês', format_number(integrated['commits_per_month'], 2)],
        ['Linhas por Commit', format_number(integrated['lines_per_commit'], 2)],
        ['Commits Necessários para Reconstruir', format_number(integrated['commits_needed_to_rebuild'], 0)],
        ['Velocidade Real', format_number(integrated['actual_velocity'], 2)],
        ['Velocidade Estimada', format_number(integrated['estimated_velocity'], 2)],
        ['Razão de Velocidade', format_number(integrated['velocity_ratio'], 2)],
        ['Eficiência de Commits', f"{format_number(integrated['commit_efficiency'] * 100, 2)}%"],
        ['% de Mudança por Commit', f"{format_number(integrated['change_percentage_per_commit'], 2)}%"],
        ['Score de Produtividade', format_number(integrated['developer_productivity_score'], 2)],
    ]

    elements.append(create_info_table(integrated_data, 'Métricas Integradas'))
    elements.append(Spacer(1, 0.5*cm))

    # Análise de velocidade
    velocity_text = f"""
    <b>Análise de Velocidade:</b><br/>
    A razão de velocidade de <b>{format_number(integrated['velocity_ratio'], 2)}</b> indica que o projeto
    está sendo desenvolvido <b>{format_number(integrated['velocity_ratio'], 2)}x</b> mais rápido que o estimado
    pelo modelo COCOMO II. Isso pode indicar:
    <br/><br/>
    • Alta produtividade da equipe<br/>
    • Uso eficiente de ferramentas e frameworks<br/>
    • Possível subestimação da complexidade inicial<br/>
    • Reutilização de código existente
    """
    elements.append(Paragraph(velocity_text, body_style))
    elements.append(Spacer(1, 0.5*cm))

    # Gráfico comparativo
    img_buffer = create_matplotlib_chart(
        None, 'bar',
        'Comparação de Métricas',
        ['Velocidade\nReal', 'Velocidade\nEstimada', 'Razão de\nVelocidade', 'Score de\nProdutividade'],
        [integrated['actual_velocity'], integrated['estimated_velocity'],
         integrated['velocity_ratio'], integrated['developer_productivity_score']]
    )
    elements.append(Image(img_buffer, width=14*cm, height=9*cm))

    # ========== INSIGHTS DE IA ==========
    ai_insights_data = None

    # Verifica se o JSON já contém insights de IA
    if 'ai_insights' in data and data['ai_insights']:
        ai_insights_data = data['ai_insights'].get('insights')

    # Se não contém e foi solicitado, tenta gerar
    elif include_ai_insights:
        try:
            # Importa os módulos necessários
            from ai_insights import generate_ai_insights
            from models import CocomoResults

            # Reconstrói os objetos a partir do JSON
            cocomo_obj = CocomoResults(**cocomo)

            # Tenta gerar insights
            print("Gerando insights de IA...")
            ai_result = generate_ai_insights(
                cocomo=cocomo_obj,
                project_name=data.get('project_name', 'Projeto'),
                project_description=None
            )

            if ai_result.get('success'):
                ai_insights_data = ai_result.get('insights')
                print("✓ Insights de IA gerados com sucesso!")
            else:
                print(f"⚠ Não foi possível gerar insights de IA: {ai_result.get('error', 'Erro desconhecido')}")

        except Exception as e:
            print(f"⚠ Erro ao gerar insights de IA: {e}")

    # Se temos insights de IA, adiciona a seção
    if ai_insights_data:
        elements.append(PageBreak())
        elements.append(Paragraph("<b>INSIGHTS DE INTELIGÊNCIA ARTIFICIAL</b>", heading_style))
        elements.append(Spacer(1, 0.3*cm))

        ai_intro_text = """
        Esta seção apresenta análises avançadas geradas por Inteligência Artificial,
        fornecendo insights sobre o valor do código, métricas de mercado e recomendações estratégicas
        baseadas nas métricas coletadas do projeto.
        """
        elements.append(Paragraph(ai_intro_text, body_style))
        elements.append(Spacer(1, 0.5*cm))

        # Adiciona os insights formatados
        ai_elements = format_ai_insights_for_pdf(ai_insights_data, body_style)
        elements.extend(ai_elements)

    # ========== CONCLUSÃO ==========
    elements.append(PageBreak())
    elements.append(Paragraph("<b>CONCLUSÃO</b>", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    conclusion_text = f"""
    O projeto <b>{data['project_name']}</b> demonstra indicadores positivos de desenvolvimento:
    <br/><br/>
    <b>Pontos Fortes:</b><br/>
    • Score de produtividade elevado ({format_number(integrated['developer_productivity_score'], 2)})<br/>
    • Eficiência de commits de {format_number(integrated['commit_efficiency'] * 100, 2)}%<br/>
    • Velocidade de desenvolvimento {format_number(integrated['velocity_ratio'], 2)}x acima do estimado<br/>
    • Complexidade classificada como {cocomo['complexity_level']}<br/>
    <br/>
    <b>Estimativas Finais:</b><br/>
    • Custo Total: R$ {format_number(cocomo['cost_estimate_brl'], 2)}<br/>
    • Duração: {format_number(cocomo['time_months'], 2)} meses<br/>
    • Equipe: {format_number(cocomo['people_required'], 1)} desenvolvedores<br/>
    • Manutenção: {format_number(cocomo['maintenance_people'], 1)} desenvolvedores<br/>
    <br/>
    Este relatório fornece uma base sólida para tomada de decisões estratégicas sobre
    alocação de recursos, planejamento de releases e estimativas de custos do projeto.
    """

    elements.append(Paragraph(conclusion_text, body_style))

    # Gera o PDF
    doc.build(elements, canvasmaker=NumberedCanvas)

    return output_pdf_path


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python generate_pdf_report.py <arquivo_json> [arquivo_pdf_saida]")
        print("\nExemplo:")
        print("  python generate_pdf_report.py reports/relatorio.json")
        print("  python generate_pdf_report.py reports/relatorio.json output.pdf")
        sys.exit(1)

    json_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(json_file).exists():
        print(f"Erro: Arquivo '{json_file}' não encontrado!")
        sys.exit(1)

    try:
        print(f"Gerando relatório PDF a partir de '{json_file}'...")
        output_path = generate_pdf_report(json_file, output_pdf)
        print(f"✓ Relatório gerado com sucesso: {output_path}")
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
