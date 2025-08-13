from typing import Any

from bs4 import BeautifulSoup
from emoji import replace_emoji


class Pipeline:
    """
    `pipe = Pipeline(f, g, h); pipe(v) ~ h(g(f(v)))`
    """

    def __init__(self, *funcs) -> None:
        self.funcs = funcs

    def __call__(self, r: Any) -> Any:
        for func in self.funcs:
            r = func(r)
        return r


remove_tags = lambda html: BeautifulSoup(html, "html.parser").text
clean_text_pipe = Pipeline(
    remove_tags,
    remove_tags,  # yes, twice
    replace_emoji,
    str.strip
)
