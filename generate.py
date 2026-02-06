from __future__ import annotations

import json
from pathlib import Path
from fnmatch import fnmatch

import yaml
from jinja2 import Environment, FileSystemLoader
from jinja_markdown2 import MarkdownExtension  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field


ICONS = {
    'github.com': 'fa-brands fa-github',
    'gitlab.com': 'fa-brands fa-gitlab',
    'codeberg.org': 'fa-solid fa-code-branch',
    '*.itch.io': 'fa-brands fa-itch-io',
    'home': 'fa-solid fa-home',
    'homepage': 'fa-solid fa-home',
}


def get_icon(name: str, url: str) -> str | None:
    icon = ICONS.get(name)
    if icon is not None:
        return icon
    url = url.removeprefix('https://')
    url = url.split('/')[0]
    icon = ICONS.get(url)
    if icon is not None:
        return icon
    for pattern, icon in ICONS.items():
        if fnmatch(url, pattern):
            return icon
    return None


class Category(BaseModel):
    group_slug: str = Field(pattern=r'^[a-z-]{3,}$')
    slug: str = Field(pattern=r'^[a-zA-Z0-9-]{1,}$')
    name: str = Field(min_length=1)
    icon: str | None = Field(pattern=r'^fa.+$', default=None)

    model_config = ConfigDict(extra='forbid')

    @property
    def full_slug(self) -> str:
        return f'{self.group_slug}/{self.slug}'


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

    @property
    def splash(self) -> str | None:
        path = Path(__file__).parent / 'splash' / f'{self.id}.png'
        if path.exists():
            return f'./splash/{self.id}.png'
        return None

    def short_dump(self) -> dict[str, object]:
        """Get a dictionary with the most basic attributes of the app.

        Used to generate the JSON list of all apps.
        """
        return {
            'id': self.id,
            'name': self.name,
            'author': self.author.name,
            'short': self.short,
            'added': self.added,
        }


class Categories(BaseModel):
    categories: list[Category] = Field(min_length=20)

    def get(self, full_slug: str) -> Category:
        for cat in self.categories:
            if cat.full_slug == full_slug:
                return cat
        raise LookupError(f'invalid category: {full_slug}')


env = Environment(loader=FileSystemLoader('templates'))
env.add_extension(MarkdownExtension)
public_dir = Path('public')
public_dir.mkdir(exist_ok=True)


def load_apps() -> list[App]:
    apps: list[App] = []
    for app_path in Path('apps').iterdir():
        author_id, _app_id, ext = app_path.name.split('.')
        assert ext == 'yaml'
        app_raw = yaml.safe_load(app_path.read_text())
        author_path = Path('authors', f'{author_id}.yaml')
        author_raw = yaml.safe_load(author_path.read_text())
        author = Author(id=author_id, **author_raw)
        app = App(id=app_path.stem, author=author, **app_raw)
        apps.append(app)
    apps.sort(key=lambda a: a.name.lower())
    apps.sort(key=lambda a: a.added, reverse=True)
    return apps


def load_authors() -> list[Author]:
    authors: list[Author] = []
    for author_path in Path('authors').iterdir():
        author_raw = yaml.safe_load(author_path.read_text())
        author = Author(id=author_path.stem, **author_raw)
        if author.id in ('index', 'apps', 'authors'):
            raise AssertionError(f'Reserved author ID: {author.id}')
        authors.append(author)
    return authors


def load_categories() -> Categories:
    categories = []
    groups = yaml.safe_load(Path('categories.yaml').read_text())
    for group_slug, group in groups.items():
        for slug, category in group.items():
            categories.append(Category(
                group_slug=group_slug,
                slug=slug,
                **category,
            ))
    return Categories(categories=categories)


def main() -> None:
    apps = load_apps()
    authors = load_authors()
    categories = load_categories()
    out_dir = Path('public')

    # render list of apps and some other pages
    for slug in ('index', '404', 'random'):
        template = env.get_template(f'{slug}.html.j2')
        content = template.render(apps=apps)
        (out_dir / f'{slug}.html').write_text(content)

    short_apps = [a.short_dump() for a in apps]
    (out_dir / 'apps.json').write_text(json.dumps(short_apps, indent=1))

    # render page for each app
    template = env.get_template('app.html.j2')
    for app in apps:
        app_cats = [categories.get(slug) for slug in app.categories]
        content = template.render(
            app=app,
            get_icon=get_icon,
            categories=app_cats,
        )
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
