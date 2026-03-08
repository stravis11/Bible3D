# NT → OT Scripture Map

Interactive 3D visualization of New Testament scriptures connected to Old Testament scriptures.

## Data source

- OpenBible cross references: https://www.openbible.info/labs/cross-references/
- Filtered to links where the source verse is in the New Testament and the target verse is in the Old Testament.

## Files

- `docs/index.html` — browser app
- `docs/data/*.json` — generated graph data for book/chapter/verse views
- `generate_map_data.py` — regeneration script from `data/cross_references.txt`

## Run locally

```bash
cd nt-ot-map/docs
python3 -m http.server 8765
```

Then open:

- <http://127.0.0.1:8765/>

## Regenerate data

```bash
cd nt-ot-map
python3 generate_map_data.py
```
