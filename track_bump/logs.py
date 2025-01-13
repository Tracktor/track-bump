import logging
import re
from dataclasses import dataclass, field

from rich.console import Console

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
    "RELEASE_TAG_START",
    "RELEASE_TAG_END",
)

_logger = logging.getLogger("track-bump")


def init_logging(level: int = logging.WARNING):
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)
    _logger.setLevel(level)


@dataclass
class RichLogger:
    logger: logging.Logger
    console: Console = field(default_factory=Console)

    @property
    def level(self):
        return self.logger.level

    @level.setter
    def level(self, value):
        self.logger.setLevel(value)

    @property
    def disabled(self) -> bool:
        return self.logger.disabled

    @disabled.setter
    def disabled(self, value: bool):
        self.logger.disabled = value

    def can_print(self, level: int) -> bool:
        return self.level <= level and self.disabled

    def _log(
        self,
        level: int,
        msg: str,
        *args,
        **kwargs,
    ):
        if not self.disabled:
            msg = rm_markdown(msg)
        self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)
        if self.can_print(logging.DEBUG):
            self.console.print(f"[steel_blue]{msg}[/steel_blue]")

    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)
        if self.can_print(logging.INFO):
            self.console.print(msg)

    def warning(self, msg: str, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)
        if self.can_print(logging.WARNING):
            self.console.print(f"[yellow]{msg}[/yellow]")

    def error(self, msg: str, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)
        if self.can_print(logging.ERROR):
            self.console.print(f"[red]{msg}[/red]")


logger = RichLogger(logger=_logger)

_MARKDOWN_PATTERN = re.compile(r"\[\/?\w+(?:=[^\]]*)?\]")


def rm_markdown(text: str) -> str:
    """
    Removes rich-style or markdown-like tags from the input string.
    It removes tags such as [bold], [italic], [color], etc.
    """
    return _MARKDOWN_PATTERN.sub("", text)


TAG_START = "[bold][cyan]"
TAG_END = "[/cyan][/bold]"

BRANCH_START = "[bold]"
BRANCH_END = "[/bold]"

COMMIT_START = "[bold][blue]"
COMMIT_END = "[/blue][/bold]"

DRY_RUN_START = "[grey58]"
DRY_RUN_END = "[/grey58]"

RELEASE_TAG_START = "[bold][green]"
RELEASE_TAG_END = "[/green][/bold]"
