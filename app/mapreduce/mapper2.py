#!/usr/bin/env python3
import sys
import os

for line in sys.stdin:
    try:
        filepath, content = line.strip().split('\t', 1)
        doc_id = os.path.basename(filepath).split('.')[0]
        
        words = content.split()
        doc_length = len(words)
        
        # Emit: doc_id \t doc_length
        print(f"{doc_id}\t{doc_length}")
    except ValueError:
        continue 