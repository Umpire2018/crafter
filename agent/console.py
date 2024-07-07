from rich.console import Console
from rich.theme import Theme
from typing import Literal

light_theme = Theme({"info": "blue", "warning": "yellow", "error": "red"})

dark_theme = Theme(
    {"info": "bright_blue", "warning": "bright_yellow", "error": "bright_red"}
)

# Initialize the console with default theme
console = Console(theme=light_theme)


def set_theme(theme_name: Literal["light", "dark"]):
    global console
    if theme_name == "dark":
        console = Console(theme=dark_theme)
    else:
        console = Console(theme=light_theme)
