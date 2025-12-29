# catalog.fireflyzero.com

Web catalog of apps and games for [Firefly Zero](https://fireflyzero.com/) hosted at [catalog.fireflyzero.com](https://catalog.fireflyzero.com/).

## Build locally

1. [Install task](https://taskfile.dev/)
1. Run `task`
1. Open the generated page: `firefox ./public/index.html`

## Add a new app

Some things you should know:

1. You don't have to add your app into the catalog. You can distribute your app in any other way (like through [itch.io](https://itch.io/)) and people can install it without a problem.
1. It's ok if the app is not a game.

Requirements:

1. The app should feel finished and polished. Tech demos are allowed in their own category (`type/tech` or `type/demo`).
1. The app must not be hateful or offensive.
1. The app must be suitable for all ages.
1. The app (code, assets, dialogs, or anything else) must not be AI-generated. Using AI-assisted tools is fine.
1. The app should be native to Firefly Zero. Games running on an emulator (Bitsy, GameBoy, etc) are not allowed. Native ports are allowed. Emulators themselves are allowed if they can be installed and used as a standalone app.
1. You should be the app's author or have the author's permission to publish it.

How to:

1. Add a new author in [authors](./authors/).
1. Add the app in [apps](./apps/).
1. [Submit a Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

## Adding an app

Each app is a separate YAML file in the [apps](./apps/) directory. The file name must be a dot-separated author ID and app ID with `.yaml` extension. Each app has the following fields:

* `name`: The app title. Must be the same as in `firefly.toml` of your app.
* `short`: The short description (140 characters tops) of the app. It is displayed in the list of apps in the catalog.
* `desc`: The detailed description of the app. Can use Markdown syntax.
* `added`: The date when the app is added in the catalog. Put today's date. Format: `2023-12-31`.
* `download`: The link to the app download. If the app is freely available, it can be a direct link to the zip file. In that case, the app will also be installable by the firefly-cli. Otherwise, it can be a link to the app page where the app can be bought.
* `links` (optional): a mapping of additional links for the app. The key is the text to show on the button and the value is the URL. You can link there the app home page, source code, other catalogs, Mastodon account, etc.
* `icon` (optional): a [font-awesome](https://fontawesome.com/) icon to display for the app in the list of apps next to the title.

## Adding an author

Each author is a separate YAML file in the [authors](./authors/) directory. The file name must be the author ID with `.yaml` extension. Each author has the following fields:

* `name`: The author's name.
* `pronouns` (optional): The author's pronoun. For example, `he/him`, `she/her`, `they/them`, etc. If that's a team of people, the pronoun is naturally `they/them`.
* `links`: A mapping of links to author's profiles. The key is the text to display on the button and the value is the URL. Should contain at least one link. It may lead to Github, itch.io, Mastodon, Patreon, etc.
* `short`: A short intro. Displayed in the list of authors.
* `about` (optional): A longer description of the authored works, passions, etc.

## Tech stack

1. We generate web pages using a custom [Python](https://www.python.org/) script.
1. The template engine is [Jinja2](https://jinja.palletsprojects.com/en/2.10.x/).
1. The data is stored in [YAML](https://en.wikipedia.org/wiki/YAML) files.
1. For CSS styling, we use [Bootstrap](https://getbootstrap.com/). It's a bit fat (36 KB compressed) and requires divs in divs but nice looking, easy to use, and does not require using the fat NPM ecosystem.
1. For icons, we use [FontAwesome](https://fontawesome.com/).
