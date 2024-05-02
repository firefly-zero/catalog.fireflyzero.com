from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from jinja_markdown2 import MarkdownExtension  # type: ignore[import-untyped]
from pydantic import BaseModel, Field


class App(BaseModel):
    id: str = Field(pattern=r'.{1,16}\..{1,16}')
    name: str = Field(min_length=2, max_length=40)
    author: str = Field(min_length=2, max_length=40)
    short: str = Field(min_length=4, max_length=140)
    added: str = Field(pattern=r'20[234][0-9]-[01][0-9]-[0123][0-9]')
    repo: str | None = Field(pattern=r'https://.+\..+', default=None)
    download: str = Field(pattern=r'https://.+\..+')
    desc: str = Field(min_length=10, max_length=10_000)


env = Environment(loader=FileSystemLoader('templates'))
env.add_extension(MarkdownExtension)
public_dir = Path('public')
public_dir.mkdir(exist_ok=True)

apps = yaml.safe_load(Path('apps.yaml').read_text())
apps = [App(id=id, **info) for id, info in apps.items()]
apps.sort(key=lambda a: (a.added, a.name), reverse=True)

template = env.get_template('index.html.j2')
content = template.render(apps=apps)
Path('public', 'index.html').write_text(content)
