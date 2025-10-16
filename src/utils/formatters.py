"""Funções utilitárias para formatação de valores."""

from __future__ import annotations


def format_number(value: float | int, decimals: int = 2) -> str:
    """
    Formata número com separadores de milhares no padrão brasileiro.

    Args:
        value: Valor numérico a ser formatado
        decimals: Número de casas decimais (padrão: 2)

    Returns:
        String formatada com separadores brasileiros (. para milhares, , para decimais)

    Examples:
        >>> format_number(1234.56)
        '1.234,56'
        >>> format_number(1234567, 0)
        '1.234.567'
        >>> format_number(0.5, 1)
        '0,5'
    """
    if not isinstance(value, (int, float)):
        return str(value)

    if decimals == 0:
        return f"{value:,.0f}".replace(',', '.')

    # Formata com decimais e substitui separadores
    formatted = f"{value:,.{decimals}f}"
    # Troca vírgula por X temporariamente, ponto por vírgula, X por ponto
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')


def format_currency(value: float, currency: str = "BRL", decimals: int = 2) -> str:
    """
    Formata valor monetário com símbolo de moeda.

    Args:
        value: Valor monetário
        currency: Código da moeda (padrão: "BRL")
        decimals: Casas decimais (padrão: 2)

    Returns:
        String formatada com símbolo e valor

    Examples:
        >>> format_currency(1500.50)
        'R$ 1.500,50'
        >>> format_currency(1000000)
        'R$ 1.000.000,00'
        >>> format_currency(99.9, "USD")
        '$ 99,90'
    """
    currency_symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = currency_symbols.get(currency.upper(), currency)
    formatted_value = format_number(value, decimals)

    return f"{symbol} {formatted_value}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formata valor como porcentagem.

    Args:
        value: Valor a ser formatado (0-100)
        decimals: Casas decimais (padrão: 1)

    Returns:
        String formatada com símbolo de porcentagem

    Examples:
        >>> format_percentage(45.5)
        '45,5%'
        >>> format_percentage(100, 0)
        '100%'
        >>> format_percentage(0.5, 2)
        '0,50%'
    """
    formatted = format_number(value, decimals)
    return f"{formatted}%"


def format_kloc(lines: int) -> str:
    """
    Formata linhas de código como KLOC (milhares de linhas).

    Args:
        lines: Número de linhas de código

    Returns:
        String formatada em KLOC

    Examples:
        >>> format_kloc(1000)
        '1.00 KLOC'
        >>> format_kloc(12345)
        '12.35 KLOC'
        >>> format_kloc(500)
        '0.50 KLOC'
    """
    kloc = lines / 1000.0
    return f"{format_number(kloc, 2)} KLOC"


def format_person_months(value: float) -> str:
    """
    Formata esforço em pessoa-meses.

    Args:
        value: Esforço em pessoa-meses

    Returns:
        String formatada

    Examples:
        >>> format_person_months(12.5)
        '12,50 pessoa-meses'
        >>> format_person_months(1)
        '1,00 pessoa-mês'
    """
    suffix = "pessoa-mês" if value <= 1 else "pessoa-meses"
    return f"{format_number(value, 2)} {suffix}"


def format_duration_months(value: float) -> str:
    """
    Formata duração em meses.

    Args:
        value: Duração em meses

    Returns:
        String formatada

    Examples:
        >>> format_duration_months(6.5)
        '6,50 meses'
        >>> format_duration_months(1)
        '1,00 mês'
    """
    suffix = "mês" if value <= 1 else "meses"
    return f"{format_number(value, 2)} {suffix}"


def format_people_count(value: float) -> str:
    """
    Formata contagem de pessoas/desenvolvedores.

    Args:
        value: Número de pessoas

    Returns:
        String formatada

    Examples:
        >>> format_people_count(3.5)
        '3,50 desenvolvedores'
        >>> format_people_count(1)
        '1,00 desenvolvedor'
    """
    suffix = "desenvolvedor" if value <= 1 else "desenvolvedores"
    return f"{format_number(value, 2)} {suffix}"


def format_file_path(path: str, max_length: int = 60) -> str:
    """
    Trunca caminho de arquivo se for muito longo.

    Args:
        path: Caminho do arquivo
        max_length: Comprimento máximo (padrão: 60)

    Returns:
        Caminho truncado se necessário

    Examples:
        >>> format_file_path("/muito/longo/caminho/para/arquivo.py", 20)
        '...o/arquivo.py'
        >>> format_file_path("curto.py", 20)
        'curto.py'
    """
    if len(path) <= max_length:
        return path

    # Mantém a parte final do caminho
    truncated = "..." + path[-(max_length - 3):]
    return truncated


def format_compact_number(value: float) -> str:
    """
    Formata número de forma compacta (K, M, B).

    Args:
        value: Valor numérico

    Returns:
        String formatada de forma compacta

    Examples:
        >>> format_compact_number(1500)
        '1.5K'
        >>> format_compact_number(1500000)
        '1.5M'
        >>> format_compact_number(500)
        '500'
    """
    if value >= 1_000_000_000:
        return f"{format_number(value / 1_000_000_000, 1)}B"
    elif value >= 1_000_000:
        return f"{format_number(value / 1_000_000, 1)}M"
    elif value >= 1_000:
        return f"{format_number(value / 1_000, 1)}K"
    else:
        return format_number(value, 0)
