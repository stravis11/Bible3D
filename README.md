# NT → OT Scripture Map

Interactive 3D visualization of New Testament scriptures connected to Old Testament scriptures.

Live: <https://stravis11.github.io/Bible3D/>

Click any book, chapter or verse to see what it connects to (with KJV text for verses), then click a connection to follow it.

## Data source

- OpenBible cross references: https://www.openbible.info/labs/cross-references/
- Filtered to links where the source verse is in the New Testament and the target verse is in the Old Testament.

## Files

- `docs/index.html` — browser app
- `docs/vendor/` — pinned copy of [3d-force-graph](https://github.com/vasturiano/3d-force-graph) 1.80.1 (MIT), so a CDN update can't break the page
- `docs/data/*.json` — generated graph data for book/chapter/verse views
- `generate_map_data.py` — regeneration script from `data/cross_references.txt`

## Run locally

```bash
cd docs
python3 -m http.server 8765
```

Then open:

- <http://127.0.0.1:8765/>

## Regenerate data

```bash
python3 generate_map_data.py
```
