# catalog.fireflyzero.com

Web catalog of apps and games for [Firefly Zero](https://fireflyzero.com/) hosted at [catalog.fireflyzero.com](https://catalog.fireflyzero.com/).

## Build locally

1. [Install task](https://taskfile.dev/)
1. Run `task`
1. Open the generated page: `firefox ./public/index.html`

## Add a new app

Things you should know:

1. You don't have to add your app into the catalog. You can distribute your app in any other way (like through [itch.io](https://itch.io/)) and people can install it without a problem.
1. The app should feel finished and polished.
1. It's ok if the app is not a game.
1. The app must not be hateful or offensive.
1. The app must be suitable for all ages.

How to:

1. Add a new author in [authors](./authors/).
1. Add the app in [apps](./apps/).
1. [Submit a Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

## Tech stack

1. We generate web pages using a custom [Python](https://www.python.org/) script.
1. The template engine is [Jinja2](https://jinja.palletsprojects.com/en/2.10.x/).
1. The data is stored in [YAML](https://en.wikipedia.org/wiki/YAML) files.
1. For CSS styling, we use [Bootstrap](https://getbootstrap.com/). It's a bit fat (36 KB compressed) and requires divs in divs but nice looking, easy to use, and does not require using the fat NPM ecosystem.
1. For icons, we use [FontAwesome](https://fontawesome.com/).
