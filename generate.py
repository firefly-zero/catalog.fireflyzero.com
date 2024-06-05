from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from jinja_markdown2 import MarkdownExtension  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field


class Author(BaseModel):
    id: str = Field(pattern=r'^.{1,16}$')
    name: str = Field(min_length=2, max_length=40)
    pronouns: str | None = Field(pattern='^[a-z]{1,8}/[a-z]{1,8}$')
    links: dict[str, str] = Field(min_length=1, max_length=16)
    about: str = Field(min_length=10, max_length=10_000)

    model_config = ConfigDict(extra='forbid')


class App(BaseModel):
    id: str = Field(pattern=r'^.{1,16}\..{1,16}$')
    name: str = Field(min_length=2, max_length=40)
    author: Author
    short: str = Field(min_length=4, max_length=140)
    added: str = Field(pattern=r'^20[234][0-9]-[01][0-9]-[0123][0-9]$')
    repo: str | None = Field(pattern=r'^https://.+\.', default=None)
    download: str = Field(pattern=r'^https://.+\.')
    desc: str = Field(min_length=10, max_length=10_000)

    model_config = ConfigDict(extra='forbid')

    @property
    def direct(self) -> bool:
        """True if the download link is a direct download for the file.
        """
        return self.download.endswith('.zip')


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


def load_authors() -> list[Author]:
    authors = []
    for author_path in Path('authors').iterdir():
        author_raw = yaml.safe_load(author_path.read_text())
        author = Author(id=author_path.stem, **author_raw)
        authors.append(author)
    return authors


apps = load_apps()
authors = load_authors()

template = env.get_template('index.html.j2')
content = template.render(apps=apps)
out_dir = Path('public')
(out_dir / 'index.html').write_text(content)

template = env.get_template('app.html.j2')
for app in apps:
    content = template.render(app=app)
    (out_dir / f'{app.id}.html').write_text(content)
    (out_dir / f'{app.id}.json').write_text(app.model_dump_json())

template = env.get_template('author.html.j2')
for author in authors:
    author_apps = [app for app in apps if app.author.id == author.id]
    content = template.render(author=author, apps=author_apps)
    (out_dir / f'{author.id}.html').write_text(content)
    (out_dir / f'{author.id}.json').write_text(author.model_dump_json())
