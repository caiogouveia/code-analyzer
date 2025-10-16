#!/usr/bin/env python3
"""
Módulo de Análise de Segurança usando Semgrep
Analisa vulnerabilidades, bad practices e problemas de segurança no código
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from models import SecurityFinding, SecurityMetrics
from utils.score_calculator import calculate_security_score
from analysis_config import (
    SEMGREP_SEVERITY_MAP,
    SEMGREP_TIMEOUT_SECONDS,
    SEMGREP_FILE_TIMEOUT_SECONDS,
    SEMGREP_MAX_FILE_SIZE_MB,
    DEFAULT_MAX_SECURITY_FINDINGS,
)


class SecurityAnalyzer:
    """Analisador de segurança usando Semgrep"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.metrics = SecurityMetrics()

    def check_semgrep_available(self) -> bool:
        """Verifica se o Semgrep está disponível no sistema"""
        try:
            result = subprocess.run(
                ['semgrep', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def analyze(self, config: str = "auto", max_findings: int = DEFAULT_MAX_SECURITY_FINDINGS) -> SecurityMetrics:
        """
        Executa análise de segurança usando Semgrep

        Args:
            config: Configuração do Semgrep a usar
                - 'auto': Detecção automática baseada na linguagem
                - 'p/security-audit': Regras de auditoria de segurança
                - 'p/owasp-top-ten': OWASP Top 10
                - 'p/python': Regras específicas para Python
                - 'p/javascript': Regras específicas para JavaScript
                - ou path para arquivo de configuração customizado
            max_findings: Número máximo de descobertas para processar

        Returns:
            SecurityMetrics com resultados da análise
        """

        if not self.check_semgrep_available():
            raise RuntimeError("Semgrep não está instalado ou não está disponível no PATH")

        self.metrics.scan_timestamp = datetime.now().isoformat()
        start_time = datetime.now()

        # Prepara comando do Semgrep
        cmd = [
            'semgrep',
            '--config', config,
            '--json',
            '--max-target-bytes', f'{SEMGREP_MAX_FILE_SIZE_MB}MB',
            '--timeout', str(SEMGREP_FILE_TIMEOUT_SECONDS),
            '--quiet',  # Menos verbose
            str(self.project_path)
        ]

        try:
            # Executa Semgrep
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SEMGREP_TIMEOUT_SECONDS
            )

            # Parse do resultado JSON
            if result.stdout:
                semgrep_data = json.loads(result.stdout)
                self._process_semgrep_results(semgrep_data, max_findings)

            # Calcula duração
            end_time = datetime.now()
            self.metrics.scan_duration_seconds = (end_time - start_time).total_seconds()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout ao executar Semgrep - Projeto muito grande ou análise muito demorada")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Erro ao parsear resultado do Semgrep: {e}")
        except Exception as e:
            raise RuntimeError(f"Erro ao executar Semgrep: {e}")

        return self.metrics

    def _process_semgrep_results(self, semgrep_data: Dict, max_findings: int):
        """Processa os resultados do Semgrep e popula as métricas"""

        results = semgrep_data.get('results', [])

        # Processa cada finding
        for idx, result in enumerate(results):
            if idx >= max_findings:
                break

            # Extrai informações
            rule_id = result.get('check_id', 'unknown')
            severity = self._normalize_severity(result.get('extra', {}).get('severity', 'INFO'))
            message = result.get('extra', {}).get('message', 'No message')

            # Metadata adicional
            extra = result.get('extra', {})
            metadata = extra.get('metadata', {})

            # Informações de localização
            path = result.get('path', '')
            start_line = result.get('start', {}).get('line', 0)

            # Código afetado
            code_lines = result.get('extra', {}).get('lines', '')

            # CWE e OWASP
            cwe = None
            owasp = None

            if 'cwe' in metadata:
                cwe_list = metadata['cwe']
                if isinstance(cwe_list, list) and cwe_list:
                    cwe = cwe_list[0]
                elif isinstance(cwe_list, str):
                    cwe = cwe_list

            if 'owasp' in metadata:
                owasp_list = metadata['owasp']
                if isinstance(owasp_list, list) and owasp_list:
                    owasp = owasp_list[0]
                elif isinstance(owasp_list, str):
                    owasp = owasp_list

            # Categoria
            category = metadata.get('category', 'unknown')
            confidence = metadata.get('confidence', 'HIGH')

            # Cria finding
            finding = SecurityFinding(
                rule_id=rule_id,
                severity=severity,
                category=category,
                message=message,
                file_path=path,
                line=start_line,
                code_snippet=code_lines,
                cwe=cwe,
                owasp=owasp,
                confidence=confidence
            )

            self.metrics.findings.append(finding)

            # Atualiza contadores
            self._update_metrics(finding)

        # Total de findings
        self.metrics.total_findings = len(self.metrics.findings)

        # Informações adicionais do scan
        if 'paths' in semgrep_data:
            scanned = semgrep_data['paths'].get('scanned', [])
            self.metrics.files_scanned = len(scanned)

        if 'errors' in semgrep_data:
            # Podemos adicionar tracking de erros aqui se necessário
            pass

    def _normalize_severity(self, severity: str) -> str:
        """Normaliza a severidade para um padrão consistente"""
        return SEMGREP_SEVERITY_MAP.get(severity.upper(), severity.upper())

    def _update_metrics(self, finding: SecurityFinding):
        """Atualiza as métricas com base em uma nova descoberta"""

        # Contadores de severidade
        if finding.severity == 'CRITICAL':
            self.metrics.critical_findings += 1
        elif finding.severity == 'HIGH':
            self.metrics.high_findings += 1
        elif finding.severity == 'MEDIUM':
            self.metrics.medium_findings += 1
        elif finding.severity == 'LOW':
            self.metrics.low_findings += 1
        else:
            self.metrics.info_findings += 1

        # Contadores de categoria
        if 'security' in finding.category.lower():
            self.metrics.security_issues += 1
        elif 'best-practice' in finding.category.lower():
            self.metrics.best_practice_issues += 1
        elif 'performance' in finding.category.lower():
            self.metrics.performance_issues += 1

        # CWE
        if finding.cwe:
            cwe_key = finding.cwe
            self.metrics.cwe_categories[cwe_key] = self.metrics.cwe_categories.get(cwe_key, 0) + 1

        # OWASP
        if finding.owasp:
            owasp_key = finding.owasp
            self.metrics.owasp_categories[owasp_key] = self.metrics.owasp_categories.get(owasp_key, 0) + 1

        # Arquivos com problemas
        file_key = finding.file_path
        self.metrics.files_with_issues[file_key] = self.metrics.files_with_issues.get(file_key, 0) + 1

    def get_security_score(self) -> float:
        """
        Calcula um score de segurança de 0-100
        100 = sem problemas
        0 = muitos problemas críticos
        """
        return calculate_security_score(self.metrics)

    def get_top_vulnerable_files(self, limit: int = 10) -> List[tuple]:
        """Retorna os arquivos mais vulneráveis"""
        sorted_files = sorted(
            self.metrics.files_with_issues.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_files[:limit]

    def get_summary(self) -> str:
        """Retorna um resumo textual da análise de segurança"""
        if self.metrics.total_findings == 0:
            return "✅ Nenhum problema de segurança encontrado!"

        score = self.get_security_score()

        summary = f"""
ANÁLISE DE SEGURANÇA - Score: {score:.1f}/100

Total de Descobertas: {self.metrics.total_findings}
  • Críticas: {self.metrics.critical_findings}
  • Altas: {self.metrics.high_findings}
  • Médias: {self.metrics.medium_findings}
  • Baixas: {self.metrics.low_findings}
  • Info: {self.metrics.info_findings}

Por Categoria:
  • Segurança: {self.metrics.security_issues}
  • Best Practices: {self.metrics.best_practice_issues}
  • Performance: {self.metrics.performance_issues}

Arquivos Escaneados: {self.metrics.files_scanned}
Tempo de Scan: {self.metrics.scan_duration_seconds:.2f}s
        """

        return summary.strip()


def main():
    """Função de teste"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python security_analyzer.py <path_do_projeto>")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()

    if not project_path.exists() or not project_path.is_dir():
        print(f"Erro: '{project_path}' não é um diretório válido")
        sys.exit(1)

    print(f"Analisando segurança de: {project_path}\n")

    analyzer = SecurityAnalyzer(project_path)

    try:
        metrics = analyzer.analyze(config='auto')
        print(analyzer.get_summary())

        print("\n\nTop 5 Arquivos Mais Vulneráveis:")
        for file_path, count in analyzer.get_top_vulnerable_files(5):
            print(f"  {file_path}: {count} problemas")

        if metrics.findings:
            print(f"\n\nPrimeiras 3 Descobertas:")
            for idx, finding in enumerate(metrics.findings[:3], 1):
                print(f"\n{idx}. [{finding.severity}] {finding.rule_id}")
                print(f"   Arquivo: {finding.file_path}:{finding.line}")
                print(f"   Mensagem: {finding.message}")

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
