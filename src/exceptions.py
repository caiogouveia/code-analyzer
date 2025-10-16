"""Exceções customizadas para o analisador COCOMO II."""

from __future__ import annotations


class CocomoAnalysisError(Exception):
    """Exceção base para erros de análise COCOMO II."""

    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class CodeAnalysisError(CocomoAnalysisError):
    """Erro ao analisar código-fonte."""
    pass


class GitAnalysisError(CocomoAnalysisError):
    """Erro ao analisar repositório Git."""

    def __init__(self, message: str, repo_path: str | None = None):
        self.repo_path = repo_path
        details = f"Repositório: {repo_path}" if repo_path else None
        super().__init__(message, details)


class SecurityAnalysisError(CocomoAnalysisError):
    """Erro ao executar análise de segurança."""

    def __init__(self, message: str, tool: str = "Semgrep"):
        self.tool = tool
        super().__init__(message, f"Ferramenta: {tool}")


class AIInsightsError(CocomoAnalysisError):
    """Erro ao gerar insights com IA."""

    def __init__(self, message: str, provider: str = "OpenAI"):
        self.provider = provider
        super().__init__(message, f"Provider: {provider}")


class InvalidProjectPathError(CocomoAnalysisError):
    """Caminho do projeto inválido ou inacessível."""

    def __init__(self, path: str, reason: str | None = None):
        self.path = path
        message = f"Caminho inválido: {path}"
        super().__init__(message, reason)


class NoCodeFilesFoundError(CodeAnalysisError):
    """Nenhum arquivo de código encontrado no diretório."""

    def __init__(self, path: str):
        self.path = path
        message = f"Nenhum arquivo de código encontrado em: {path}"
        super().__init__(message)


class GitRepositoryNotFoundError(GitAnalysisError):
    """Diretório não é um repositório Git válido."""

    def __init__(self, path: str):
        message = f"Não é um repositório Git válido: {path}"
        super().__init__(message, path)


class SemgrepNotInstalledError(SecurityAnalysisError):
    """Semgrep não está instalado ou não está disponível no PATH."""

    def __init__(self):
        message = (
            "Semgrep não está instalado ou não está disponível no PATH. "
            "Instale com: pip install semgrep"
        )
        super().__init__(message)


class AnalysisTimeoutError(CocomoAnalysisError):
    """Análise excedeu o tempo limite."""

    def __init__(self, analysis_type: str, timeout_seconds: int):
        self.analysis_type = analysis_type
        self.timeout_seconds = timeout_seconds
        message = (
            f"Análise {analysis_type} excedeu o tempo limite de {timeout_seconds}s"
        )
        super().__init__(message)


class ExportError(CocomoAnalysisError):
    """Erro ao exportar resultados."""

    def __init__(self, format_type: str, reason: str | None = None):
        self.format_type = format_type
        message = f"Erro ao exportar para {format_type}"
        super().__init__(message, reason)
