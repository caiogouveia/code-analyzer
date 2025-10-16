#!/usr/bin/env python3
"""
Módulo de Insights com IA usando OpenAI
Gera análises inteligentes sobre valor do código e métricas de mercado
"""

import os
import json
from typing import Optional, Dict, Any
from dataclasses import asdict

from openai import OpenAI
from models import CocomoResults, GitMetrics, IntegratedMetrics, CodeMetrics
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do .env

class AIInsightsGenerator:
    """Gerador de insights usando IA da OpenAI"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o gerador de insights com IA

        Args:
            api_key: Chave da API OpenAI. Se não fornecida, usa a variável de ambiente OPENAI_API_KEY
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API Key da OpenAI não fornecida. "
                "Configure a variável de ambiente OPENAI_API_KEY ou passe o parâmetro api_key"
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Modelo otimizado para custo-benefício

    def generate_insights(
        self,
        cocomo: CocomoResults,
        git: Optional[GitMetrics] = None,
        integrated: Optional[IntegratedMetrics] = None,
        code_metrics: Optional[CodeMetrics] = None,
        project_name: str = "Projeto",
        project_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera insights completos usando IA

        Args:
            cocomo: Resultados da análise COCOMO II
            git: Métricas Git (opcional)
            integrated: Métricas integradas (opcional)
            code_metrics: Métricas de código (opcional)
            project_name: Nome do projeto
            project_description: Descrição do projeto (opcional)

        Returns:
            Dict com insights estruturados
        """

        # Prepara contexto
        context = self._prepare_context(
            cocomo, git, integrated, code_metrics,
            project_name, project_description
        )

        # Gera insights
        prompt = self._build_prompt(context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um analista sênior de engenharia de software especializado em "
                            "avaliação de projetos, métricas de desenvolvimento e análise de mercado. "
                            "Forneça insights profissionais, objetivos e acionáveis baseados nos dados fornecidos."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            insights = json.loads(result_text)

            return {
                "success": True,
                "insights": insights,
                "tokens_used": response.usage.total_tokens,
                "model": self.model
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "insights": None
            }

    def _prepare_context(
        self,
        cocomo: CocomoResults,
        git: Optional[GitMetrics],
        integrated: Optional[IntegratedMetrics],
        code_metrics: Optional[CodeMetrics],
        project_name: str,
        project_description: Optional[str]
    ) -> Dict[str, Any]:
        """Prepara o contexto com todas as métricas"""

        context = {
            "project_name": project_name,
            "project_description": project_description or "Não fornecida",
            "cocomo_metrics": {
                "kloc": cocomo.kloc,
                "complexity_level": cocomo.complexity_level,
                "effort_person_months": cocomo.effort_person_months,
                "time_months": cocomo.time_months,
                "people_required": cocomo.people_required,
                "maintenance_people": cocomo.maintenance_people,
                "expansion_people": cocomo.expansion_people,
                "productivity": cocomo.productivity,
                "cost_estimate_brl": cocomo.cost_estimate_brl,
            }
        }

        if code_metrics:
            context["code_metrics"] = {
                "total_lines": code_metrics.total_lines,
                "code_lines": code_metrics.code_lines,
                "comment_lines": code_metrics.comment_lines,
                "blank_lines": code_metrics.blank_lines,
                "files_count": code_metrics.files_count,
                "languages": code_metrics.languages,
                "comment_ratio": (
                    code_metrics.comment_lines / code_metrics.code_lines * 100
                    if code_metrics.code_lines > 0 else 0
                )
            }

        if git:
            context["git_metrics"] = {
                "total_commits": git.total_commits,
                "total_authors": git.total_authors,
                "repository_age_days": git.repository_age_days,
                "commits_per_day": git.commits_per_day,
                "total_insertions": git.total_insertions,
                "total_deletions": git.total_deletions,
                "avg_changes_per_commit": git.avg_changes_per_commit,
                "avg_files_per_commit": git.avg_files_per_commit,
            }

        if integrated:
            context["integrated_metrics"] = {
                "lines_per_commit": integrated.lines_per_commit,
                "commits_per_month": integrated.commits_per_month,
                "actual_velocity": integrated.actual_velocity,
                "estimated_velocity": integrated.estimated_velocity,
                "velocity_ratio": integrated.velocity_ratio,
                "commit_efficiency": integrated.commit_efficiency,
                "change_percentage_per_commit": integrated.change_percentage_per_commit,
                "developer_productivity_score": integrated.developer_productivity_score,
            }

        return context

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Constrói o prompt para a IA"""

        prompt = f"""
Analise as métricas do projeto de software abaixo e forneça insights profissionais e acionáveis.

PROJETO: {context['project_name']}
DESCRIÇÃO: {context['project_description']}

MÉTRICAS COCOMO II:
{json.dumps(context['cocomo_metrics'], indent=2)}
"""

        if "code_metrics" in context:
            prompt += f"""
MÉTRICAS DE CÓDIGO:
{json.dumps(context['code_metrics'], indent=2)}
"""

        if "git_metrics" in context:
            prompt += f"""
MÉTRICAS GIT:
{json.dumps(context['git_metrics'], indent=2)}
"""

        if "integrated_metrics" in context:
            prompt += f"""
MÉTRICAS INTEGRADAS:
{json.dumps(context['integrated_metrics'], indent=2)}
"""

        prompt += """

Forneça uma análise estruturada em JSON com os seguintes campos:

{
  "valor_codigo": {
    "avaliacao_geral": "string (3-4 linhas sobre o valor e qualidade geral do código)",
    "pontos_fortes": ["lista de 3-5 pontos fortes identificados"],
    "areas_melhoria": ["lista de 3-5 áreas que precisam de atenção"],
    "valor_mercado_estimado": "string (estimativa de valor de mercado baseado nas métricas)"
  },
  "metricas_mercado": {
    "comparacao_industria": "string (como este projeto se compara com padrões da indústria)",
    "maturidade_projeto": "string (nível de maturidade: inicial, em desenvolvimento, maduro, etc.)",
    "qualidade_codigo": "string (avaliação da qualidade baseada nas métricas)",
    "velocidade_desenvolvimento": "string (análise da velocidade comparada com benchmarks)",
    "custo_beneficio": "string (análise de custo-benefício do desenvolvimento)"
  },
  "recomendacoes_estrategicas": {
    "curto_prazo": ["lista de 3-5 ações recomendadas para curto prazo (1-3 meses)"],
    "medio_prazo": ["lista de 3-5 ações para médio prazo (3-6 meses)"],
    "longo_prazo": ["lista de 2-4 ações para longo prazo (6+ meses)"]
  },
  "indicadores_chave": {
    "roi_estimado": "string (estimativa de retorno sobre investimento)",
    "time_to_market": "string (avaliação do tempo até lançamento)",
    "risco_tecnico": "string (baixo/médio/alto e justificativa)",
    "escalabilidade": "string (potencial de escalabilidade do projeto)",
    "sustentabilidade": "string (sustentabilidade de longo prazo)"
  },
  "oportunidades": {
    "monetizacao": ["lista de 3-4 oportunidades de monetização"],
    "expansao": ["lista de 3-4 oportunidades de expansão"],
    "otimizacao": ["lista de 3-4 áreas de otimização com maior impacto"]
  }
}

Seja específico, baseie-se nos dados fornecidos e forneça insights acionáveis e relevantes para o contexto brasileiro de desenvolvimento de software.
"""

        return prompt

    def format_insights_for_display(self, insights: Dict[str, Any]) -> str:
        """
        Formata os insights para exibição em terminal (Rich markup)

        Args:
            insights: Dict com insights gerados pela IA

        Returns:
            String formatada com markup Rich
        """

        if not insights or "success" not in insights or not insights["success"]:
            error_msg = insights.get("error", "Erro desconhecido") if insights else "Sem insights"
            return f"[red]❌ Erro ao gerar insights: {error_msg}[/red]"

        data = insights["insights"]
        output = []

        # Valor do Código
        if "valor_codigo" in data:
            vc = data["valor_codigo"]
            output.append("[bold cyan]💎 VALOR DO CÓDIGO[/bold cyan]")
            output.append(f"\n{vc.get('avaliacao_geral', '')}\n")

            if "pontos_fortes" in vc and vc["pontos_fortes"]:
                output.append("[bold green]✓ Pontos Fortes:[/bold green]")
                for ponto in vc["pontos_fortes"]:
                    output.append(f"  • {ponto}")
                output.append("")

            if "areas_melhoria" in vc and vc["areas_melhoria"]:
                output.append("[bold yellow]⚡ Áreas de Melhoria:[/bold yellow]")
                for area in vc["areas_melhoria"]:
                    output.append(f"  • {area}")
                output.append("")

            if "valor_mercado_estimado" in vc:
                output.append(f"[bold]💰 Valor de Mercado:[/bold] {vc['valor_mercado_estimado']}")
                output.append("")

        # Métricas de Mercado
        if "metricas_mercado" in data:
            mm = data["metricas_mercado"]
            output.append("\n[bold cyan]📊 MÉTRICAS DE MERCADO[/bold cyan]")

            for key, label in [
                ("comparacao_industria", "Comparação com Indústria"),
                ("maturidade_projeto", "Maturidade do Projeto"),
                ("qualidade_codigo", "Qualidade do Código"),
                ("velocidade_desenvolvimento", "Velocidade de Desenvolvimento"),
                ("custo_beneficio", "Custo-Benefício")
            ]:
                if key in mm:
                    output.append(f"\n[bold]{label}:[/bold]")
                    output.append(f"{mm[key]}")

        # Recomendações Estratégicas
        if "recomendacoes_estrategicas" in data:
            re = data["recomendacoes_estrategicas"]
            output.append("\n\n[bold cyan]🎯 RECOMENDAÇÕES ESTRATÉGICAS[/bold cyan]")

            if "curto_prazo" in re and re["curto_prazo"]:
                output.append("\n[bold yellow]Curto Prazo (1-3 meses):[/bold yellow]")
                for rec in re["curto_prazo"]:
                    output.append(f"  • {rec}")

            if "medio_prazo" in re and re["medio_prazo"]:
                output.append("\n[bold yellow]Médio Prazo (3-6 meses):[/bold yellow]")
                for rec in re["medio_prazo"]:
                    output.append(f"  • {rec}")

            if "longo_prazo" in re and re["longo_prazo"]:
                output.append("\n[bold yellow]Longo Prazo (6+ meses):[/bold yellow]")
                for rec in re["longo_prazo"]:
                    output.append(f"  • {rec}")

        # Indicadores Chave
        if "indicadores_chave" in data:
            ik = data["indicadores_chave"]
            output.append("\n\n[bold cyan]📈 INDICADORES CHAVE[/bold cyan]")

            for key, label in [
                ("roi_estimado", "ROI Estimado"),
                ("time_to_market", "Time to Market"),
                ("risco_tecnico", "Risco Técnico"),
                ("escalabilidade", "Escalabilidade"),
                ("sustentabilidade", "Sustentabilidade")
            ]:
                if key in ik:
                    output.append(f"[bold]{label}:[/bold] {ik[key]}")

        # Oportunidades
        if "oportunidades" in data:
            op = data["oportunidades"]
            output.append("\n\n[bold cyan]💡 OPORTUNIDADES[/bold cyan]")

            if "monetizacao" in op and op["monetizacao"]:
                output.append("\n[bold green]Monetização:[/bold green]")
                for oport in op["monetizacao"]:
                    output.append(f"  • {oport}")

            if "expansao" in op and op["expansao"]:
                output.append("\n[bold green]Expansão:[/bold green]")
                for oport in op["expansao"]:
                    output.append(f"  • {oport}")

            if "otimizacao" in op and op["otimizacao"]:
                output.append("\n[bold green]Otimização:[/bold green]")
                for oport in op["otimizacao"]:
                    output.append(f"  • {oport}")

        # Rodapé
        tokens = insights.get("tokens_used", 0)
        model = insights.get("model", "unknown")
        output.append(f"\n\n[dim]Gerado por IA ({model}) • {tokens} tokens utilizados[/dim]")

        return "\n".join(output)


def generate_ai_insights(
    cocomo: CocomoResults,
    git: Optional[GitMetrics] = None,
    integrated: Optional[IntegratedMetrics] = None,
    code_metrics: Optional[CodeMetrics] = None,
    project_name: str = "Projeto",
    project_description: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função utilitária para gerar insights com IA

    Args:
        cocomo: Resultados COCOMO II
        git: Métricas Git (opcional)
        integrated: Métricas integradas (opcional)
        code_metrics: Métricas de código (opcional)
        project_name: Nome do projeto
        project_description: Descrição do projeto
        api_key: Chave API OpenAI (usa env var se não fornecida)

    Returns:
        Dict com insights gerados
    """
    try:
        generator = AIInsightsGenerator(api_key=api_key)
        return generator.generate_insights(
            cocomo=cocomo,
            git=git,
            integrated=integrated,
            code_metrics=code_metrics,
            project_name=project_name,
            project_description=project_description
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "insights": None
        }
