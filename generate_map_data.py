from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'cross_references.txt'
OUT = ROOT / 'docs' / 'data'
OUT.mkdir(parents=True, exist_ok=True)

OT_BOOKS = [
    'Gen','Exod','Lev','Num','Deut','Josh','Judg','Ruth','1Sam','2Sam','1Kgs','2Kgs','1Chr','2Chr',
    'Ezra','Neh','Esth','Job','Ps','Prov','Eccl','Song','Isa','Jer','Lam','Ezek','Dan','Hos','Joel',
    'Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal'
]
NT_BOOKS = [
    'Matt','Mark','Luke','John','Acts','Rom','1Cor','2Cor','Gal','Eph','Phil','Col','1Thess','2Thess',
    '1Tim','2Tim','Titus','Phlm','Heb','Jas','1Pet','2Pet','1John','2John','3John','Jude','Rev'
]

OT_SET = set(OT_BOOKS)
NT_SET = set(NT_BOOKS)

BOOK_GROUPS = {
    'Pentateuch': {'Gen','Exod','Lev','Num','Deut'},
    'History': {'Josh','Judg','Ruth','1Sam','2Sam','1Kgs','2Kgs','1Chr','2Chr','Ezra','Neh','Esth'},
    'Wisdom': {'Job','Ps','Prov','Eccl','Song'},
    'Major Prophets': {'Isa','Jer','Lam','Ezek','Dan'},
    'Minor Prophets': {'Hos','Joel','Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal'},
    'Gospels': {'Matt','Mark','Luke','John'},
    'Acts': {'Acts'},
    'Pauline Epistles': {'Rom','1Cor','2Cor','Gal','Eph','Phil','Col','1Thess','2Thess','1Tim','2Tim','Titus','Phlm'},
    'General Epistles': {'Heb','Jas','1Pet','2Pet','1John','2John','3John','Jude'},
    'Apocalypse': {'Rev'},
}

BOOK_ORDER = OT_BOOKS + NT_BOOKS
BOOK_INDEX = {book: idx for idx, book in enumerate(BOOK_ORDER)}


def parse_ref(ref: str):
    start = ref.split('-')[0]
    parts = start.split('.')
    book = parts[0]
    chapter = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
    verse = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
    return book, chapter, verse


def book_group(book: str) -> str:
    for group, books in BOOK_GROUPS.items():
        if book in books:
            return group
    return 'Other'

book_edges = Counter()
chapter_edges = Counter()
verse_edges = Counter()
node_weight = Counter()

with DATA.open() as f:
    next(f)
    for line in f:
        from_ref, to_ref, votes, *_ = line.strip().split('\t')
        votes = int(votes)
        from_book, from_ch, from_vs = parse_ref(from_ref)
        to_book, to_ch, to_vs = parse_ref(to_ref)
        if from_book not in NT_SET or to_book not in OT_SET:
            continue
        book_edges[(from_book, to_book)] += votes
        chapter_edges[(f'{from_book}.{from_ch}', f'{to_book}.{to_ch}')] += votes
        verse_edges[(f'{from_book}.{from_ch}.{from_vs}', f'{to_book}.{to_ch}.{to_vs}')] += votes
        node_weight[from_book] += votes
        node_weight[to_book] += votes
        node_weight[f'{from_book}.{from_ch}'] += votes
        node_weight[f'{to_book}.{to_ch}'] += votes
        node_weight[f'{from_book}.{from_ch}.{from_vs}'] += votes
        node_weight[f'{to_book}.{to_ch}.{to_vs}'] += votes


def build_nodes(edges: Counter, level: str):
    ids = set()
    for s, t in edges:
        ids.add(s)
        ids.add(t)
    nodes = []
    for node_id in ids:
        book, chapter, verse = parse_ref(node_id)
        testament = 'OT' if book in OT_SET else 'NT'
        nodes.append({
            'id': node_id,
            'label': node_id.replace('.', ' '),
            'book': book,
            'chapter': chapter,
            'verse': verse,
            'testament': testament,
            'group': book_group(book),
            'weight': node_weight[node_id],
            'order': BOOK_INDEX.get(book, 999),
            'kind': level,
        })
    return sorted(nodes, key=lambda n: (n['testament'], n['order'], n['chapter'] or 0, n['verse'] or 0))


def build_links(edges: Counter):
    links = []
    for (source, target), weight in edges.items():
        links.append({'source': source, 'target': target, 'weight': weight})
    return sorted(links, key=lambda l: l['weight'], reverse=True)

summary = {
    'book': {'nodes': build_nodes(book_edges, 'book'), 'links': build_links(book_edges)},
    'chapter': {'nodes': build_nodes(chapter_edges, 'chapter'), 'links': build_links(chapter_edges)},
    'verse': {'nodes': build_nodes(verse_edges, 'verse'), 'links': build_links(verse_edges)},
}

for level, payload in summary.items():
    (OUT / f'{level}.json').write_text(json.dumps(payload, separators=(',', ':')))

stats = {
    'bookLinks': len(summary['book']['links']),
    'chapterLinks': len(summary['chapter']['links']),
    'verseLinks': len(summary['verse']['links']),
    'bookTopLinks': summary['book']['links'][:20],
    'chapterTopLinks': summary['chapter']['links'][:20],
    'verseTopLinks': summary['verse']['links'][:20],
}
(OUT / 'stats.json').write_text(json.dumps(stats, indent=2))
print(json.dumps(stats, indent=2))
