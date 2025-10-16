"""Configuração centralizada de logging para o projeto."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


# Configuração de formato de log
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logger(
    name: str = "cocomo_analyzer",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Configura e retorna um logger para o projeto.

    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho opcional para arquivo de log
        console: Se True, também exibe logs no console

    Returns:
        Logger configurado

    Examples:
        >>> logger = setup_logger("meu_modulo", level=logging.DEBUG)
        >>> logger.info("Mensagem informativa")
        >>> logger.error("Erro detectado", exc_info=True)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()

    # Formador padrão
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Handler para console
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Handler para arquivo (opcional)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Evita propagação para o root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger existente ou cria um novo com configurações padrão.

    Args:
        name: Nome do logger (geralmente __name__ do módulo)

    Returns:
        Logger configurado

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("Iniciando análise")
    """
    logger = logging.getLogger(name)

    # Se o logger ainda não tem handlers, configura com padrões
    if not logger.handlers:
        return setup_logger(name)

    return logger


def set_log_level(logger: logging.Logger, level: int) -> None:
    """
    Altera o nível de log de um logger e seus handlers.

    Args:
        logger: Logger a ser configurado
        level: Novo nível de log

    Examples:
        >>> logger = get_logger(__name__)
        >>> set_log_level(logger, logging.DEBUG)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


# Logger padrão do projeto
default_logger = setup_logger()


# Atalhos para facilitar uso direto
def debug(msg: str, *args, **kwargs):
    """Log de debug usando o logger padrão."""
    default_logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log de info usando o logger padrão."""
    default_logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log de warning usando o logger padrão."""
    default_logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log de error usando o logger padrão."""
    default_logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log de critical usando o logger padrão."""
    default_logger.critical(msg, *args, **kwargs)
