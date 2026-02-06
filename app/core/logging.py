"""Configuracao simples de logging."""
import logging
from typing import Optional


def init_logging(level: str = "INFO") -> None:
    """Inicializa o logging padrao da aplicacao."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Obtem logger configurado para o modulo informado."""
    return logging.getLogger(name)
