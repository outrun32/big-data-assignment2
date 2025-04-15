#!/usr/bin/env python3
import sys
from collections import defaultdict
from typing import Dict, List, DefaultDict

current_term: str | None = None
TermInfo = Dict[str, List[int] | int]
term_docs: DefaultDict[str, TermInfo] = defaultdict(lambda: {'positions': [], 'tf': 0})

for line in sys.stdin:
    try:
        term, doc_id, position, freq = line.strip().split('\t')
        position = int(position)
        freq = int(freq)
    except ValueError:
        continue

    if current_term and current_term != term:
        for doc_id in term_docs:
            positions_list: List[int] = term_docs[doc_id]['positions'] # type: ignore
            tf_count: int = term_docs[doc_id]['tf'] # type: ignore
            positions_str = ','.join(map(str, positions_list))
            print(f"{current_term}\t{doc_id}\t{tf_count}\t{positions_str}")
        term_docs = defaultdict(lambda: {'positions': [], 'tf': 0})

    current_term = term
    term_docs[doc_id]['positions'].append(position) # type: ignore
    term_docs[doc_id]['tf'] += freq # type: ignore

if current_term:
    for doc_id in term_docs:
        positions_list: List[int] = term_docs[doc_id]['positions'] # type: ignore
        tf_count: int = term_docs[doc_id]['tf'] # type: ignore
        positions_str = ','.join(map(str, positions_list))
        print(f"{current_term}\t{doc_id}\t{tf_count}\t{positions_str}")