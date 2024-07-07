from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from jinja_markdown2 import MarkdownExtension  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field


ICONS = {
    'github.com': 'fa-brands fa-github',
    'gitlab.com': 'fa-brands fa-gitlab',
    'home': 'fa-solid fa-home',
    'homepage': 'fa-solid fa-home',
}


def get_icon(name: str, url: str) -> str | None:
    icon = ICONS.get(name)
    if icon is not None:
        return icon
    url = url.removeprefix('https://')
    url = url.split('/')[0]
    return ICONS.get(url)


class Category(BaseModel):
    group_slug: str = Field(pattern=r'^[a-z-]{3,}$')
    slug: str = Field(pattern=r'^[a-zA-Z0-9-]{1,}$')
    name: str = Field(min_length=1)


class Author(BaseModel):
    id: str = Field(pattern=r'^.{1,16}$')
    name: str = Field(min_length=2, max_length=40)
    pronouns: str | None = Field(
        pattern=r'^[a-z]{1,8}/[a-z]{1,8}$', default=None,
    )
    links: dict[str, str] = Field(min_length=1, max_length=16)
    short: str = Field(min_length=4, max_length=140)
    about: str | None = Field(min_length=10, max_length=10_000, default=None)

    model_config = ConfigDict(extra='forbid')


class App(BaseModel):
    id: str = Field(pattern=r'^.{1,16}\..{1,16}$')
    name: str = Field(min_length=2, max_length=40)
    author: Author
    short: str = Field(min_length=4, max_length=140)
    added: str = Field(pattern=r'^20[234][0-9]-[01][0-9]-[0123][0-9]$')
    download: str = Field(pattern=r'^https://.+\.')
    links: dict[str, str] | None = Field(max_length=16, default=None)
    icon: str | None = Field(pattern=r'^fa-', default=None)
    categories: list[str] = Field(min_length=1)
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


def load_categories() -> list[Category]:
    categories = []
    groups = yaml.safe_load(Path('categories.yaml').read_text())
    for group_slug, group in groups.items():
        for slug, category in group.items():
            categories.append(Category(
                group_slug=group_slug,
                slug=slug,
                **category,
            ))
    return categories


def main() -> None:
    apps = load_apps()
    authors = load_authors()
    categories = load_categories()
    out_dir = Path('public')

    # render list of apps
    template = env.get_template('index.html.j2')
    content = template.render(apps=apps)
    (out_dir / 'index.html').write_text(content)

    # render page for each app
    template = env.get_template('app.html.j2')
    for app in apps:
        content = template.render(app=app, get_icon=get_icon)
        (out_dir / f'{app.id}.html').write_text(content)
        (out_dir / f'{app.id}.json').write_text(app.model_dump_json())

    # render list of authors
    template = env.get_template('authors.html.j2')
    content = template.render(authors=authors)
    (out_dir / 'authors.html').write_text(content)

    # render page for each author
    template = env.get_template('author.html.j2')
    for author in authors:
        author_apps = [app for app in apps if app.author.id == author.id]
        content = template.render(
            author=author,
            apps=author_apps,
            get_icon=get_icon,
        )
        (out_dir / f'{author.id}.html').write_text(content)
        (out_dir / f'{author.id}.json').write_text(author.model_dump_json())


main()
