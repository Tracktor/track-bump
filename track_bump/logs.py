import logging
from rich.console import Console
from dataclasses import dataclass
import re

__all__ = (
    "logger",
    "init_logging",
    "TAG_START",
    "TAG_END",
    "BRANCH_START",
    "BRANCH_END",
    "COMMIT_START",
    "COMMIT_END",
    "DRY_RUN_START",
    "DRY_RUN_END",
)

_logger = logging.getLogger("track-bump")
console = Console()


def init_logging(level: int = logging.WARNING):
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)
    _logger.setLevel(level)


@dataclass
class Logger:
    level: int = logging.INFO
    log_enabled: bool = False

    def debug(self, message: str):
        _logger.debug(rm_markdown(message))
        if self.level <= logging.DEBUG and not self.log_enabled:
            console.print(f"[steel_blue]{message}[/steel_blue]")

    def info(self, message: str):
        _logger.info(rm_markdown(message))
        if self.level <= logging.INFO and not self.log_enabled:
            console.print(message)

    def warning(self, message: str):
        _logger.warning(rm_markdown(message))
        if self.level <= logging.WARNING and not self.log_enabled:
            console.print(f"[yellow]{message}[/yellow]")

    def error(self, message: str):
        _logger.error(rm_markdown(message))
        if self.level <= logging.ERROR and not self.log_enabled:
            console.print(f"[red]{message}[/red]")


logger = Logger()

TAG_START = "[bold][cyan]"
TAG_END = "[/cyan][/bold]"

BRANCH_START = "[bold]"
BRANCH_END = "[/bold]"

COMMIT_START = "[bold][blue]"
COMMIT_END = "[/blue][/bold]"

DRY_RUN_START = "[grey58]"
DRY_RUN_END = "[/grey58]"

_MARKDOWN_PATTERN = re.compile(r"\[\/?\w+(?:=[^\]]*)?\]")


def rm_markdown(text: str) -> str:
    """
    Removes rich-style or markdown-like tags from the input string.
    It removes tags such as [bold], [italic], [color], etc.
    """
    return _MARKDOWN_PATTERN.sub("", text)
