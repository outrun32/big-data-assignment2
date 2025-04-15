#!/usr/bin/env python3
import sys

doc_lengths = {}
total_docs = 0
total_length = 0

for line in sys.stdin:
    try:
        doc_id, length = line.strip().split('\t')
        length = int(length)
        
        doc_lengths[doc_id] = length
        total_docs += 1
        total_length += length
    except ValueError:
        continue

# Calculate average document length
avg_length = total_length / total_docs if total_docs > 0 else 0

print(f"STATS\t{total_docs}\t{avg_length}")

for doc_id, length in doc_lengths.items():
    print(f"DOC\t{doc_id}\t{length}") 