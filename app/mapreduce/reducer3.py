#!/usr/bin/env python3
import sys
from cassandra.cluster import Cluster

try:
    cluster = Cluster(['cassandra-server'])
    session = cluster.connect()
    
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS search_engine 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)
    
    session.execute("USE search_engine")
    
    session.execute("""
        CREATE TABLE IF NOT EXISTS term_index (
            term text,
            doc_id text,
            term_freq int,
            positions text,
            PRIMARY KEY (term, doc_id)
        )
    """)
    
    session.execute("""
        CREATE TABLE IF NOT EXISTS document_stats (
            doc_id text PRIMARY KEY,
            doc_length int
        )
    """)
    
    session.execute("""
        CREATE TABLE IF NOT EXISTS global_stats (
            id text PRIMARY KEY,
            total_docs int,
            avg_doc_length double
        )
    """)
    
    # Prepared statements for efficiency
    insert_term = session.prepare("""
        INSERT INTO term_index (term, doc_id, term_freq, positions)
        VALUES (?, ?, ?, ?)
    """)
    
    insert_doc_stats = session.prepare("""
        INSERT INTO document_stats (doc_id, doc_length)
        VALUES (?, ?)
    """)
    
    insert_global_stats = session.prepare("""
        INSERT INTO global_stats (id, total_docs, avg_doc_length)
        VALUES (?, ?, ?)
    """)
    
    for line in sys.stdin:
        parts = line.strip().split('\t')
        
        if parts[0] == "STATS":
            # Global statistics for BM25
            _, total_docs, avg_length = parts
            session.execute(insert_global_stats, ["global", int(total_docs), float(avg_length)])
            print(f"Inserted global stats: {total_docs} docs, avg length {avg_length}")
            
        elif parts[0] == "DOC":
            # Document statistics
            _, doc_id, doc_length = parts
            session.execute(insert_doc_stats, [doc_id, int(doc_length)])
            print(f"Inserted document stats for {doc_id}")
            
        else:
            # Term document index
            term, doc_id, term_freq, positions = parts
            session.execute(insert_term, [term, doc_id, int(term_freq), positions])
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
finally:
    if 'cluster' in locals():
        cluster.shutdown() 