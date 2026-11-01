from collections import Counter
from pathlib import Path
import yaml

counts = Counter[str]()
for path in (Path(__file__).parent / 'apps').iterdir():
    app = yaml.safe_load(path.read_text())
    counts.update(app['categories'])

for name, count in counts.most_common():
    if count > 2:
        print(f'{name:40} {count:>3}')
