from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from jinja_markdown2 import MarkdownExtension  # type: ignore[import-untyped]
from pydantic import BaseModel, Field


class Author(BaseModel):
    id: str = Field(pattern=r'.{1,16}')
    name: str = Field(min_length=2, max_length=40)
    github: str | None = Field(pattern=r'https://github\.com/.+')
    homepage: str | None = Field(pattern=r'https://.+\..+')


class App(BaseModel):
    id: str = Field(pattern=r'.{1,16}\..{1,16}')
    name: str = Field(min_length=2, max_length=40)
    author: Author
    short: str = Field(min_length=4, max_length=140)
    added: str = Field(pattern=r'20[234][0-9]-[01][0-9]-[0123][0-9]')
    repo: str | None = Field(pattern=r'https://.+\..+', default=None)
    download: str = Field(pattern=r'https://.+\..+')
    desc: str = Field(min_length=10, max_length=10_000)


env = Environment(loader=FileSystemLoader('templates'))
env.add_extension(MarkdownExtension)
public_dir = Path('public')
public_dir.mkdir(exist_ok=True)


def load_apps() -> list[App]:
    apps = []
    for app_path in Path('apps').iterdir():
        author_id, _app_id, ext = app_path.name.split('.')
        assert ext == 'yaml'
        app_raw = yaml.safe_load(app_path.read_text())
        author_path = Path('authors', f'{author_id}.yaml')
        author_raw = yaml.safe_load(author_path.read_text())
        author = Author(id=author_id, **author_raw)
        app = App(id=app_path.stem, author=author, **app_raw)
        apps.append(app)
    apps.sort(key=lambda a: (a.added, a.name), reverse=True)
    return apps


apps = load_apps()

template = env.get_template('index.html.j2')
content = template.render(apps=apps)
Path('public', 'index.html').write_text(content)

template = env.get_template('app.html.j2')
out_dir = Path('public')
for app in apps:
    content = template.render(app=app)
    (out_dir / f'{app.id}.html').write_text(content)
    (out_dir / f'{app.id}.json').write_text(app.model_dump_json())
