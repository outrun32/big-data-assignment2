# Big Data Assignment: Simple Search Engine Report

## Methodology

This report details the implementation of the indexing component for a simple search engine using Hadoop MapReduce and Apache Cassandra. The goal was to create a distributed system capable of indexing text documents and preparing the necessary data structures for efficient search retrieval, specifically using the BM25 ranking algorithm.

**Design Choices and Components:**

1.  **Distributed Processing Framework:** Hadoop MapReduce was chosen as the core processing framework. Its distributed nature allows for parallel processing of large document sets across a cluster, making it suitable for scalable indexing. We utilized the `hadoop-streaming` utility to allow writing MapReduce jobs in Python, facilitating easier development and integration with text processing libraries.

2.  **Indexing Pipeline:** A multi-stage MapReduce pipeline was designed to handle the indexing process:
    *   **Stage 1 (Term Extraction & Processing):**
        *   `mapper1.py`: Reads input documents (expected format: `filepath\tcontent`), extracts the `doc_id` from the filename, tokenizes the text content, converts tokens to lowercase, removes common English stopwords (using NLTK), and performs stemming using the Porter stemmer (NLTK). It emits key-value pairs of the format: `stemmed_term\tdoc_id\tposition\t1`.
        *   `reducer1.py`: Aggregates the data for each term. It groups occurrences by document, calculates the term frequency (TF) within each document, and compiles a list of positions where the term appears. It outputs: `term\tdoc_id\ttf\tcomma_separated_positions`.
    *   **Stage 2 (Document Statistics Calculation):**
        *   `mapper2.py`: Reads the original input documents again. For each document, it calculates the total number of words (document length). It emits: `doc_id\tdoc_length`.
        *   `reducer2.py`: Aggregates document lengths. It calculates the total number of documents in the corpus and the average document length across the corpus. It outputs two types of records: global statistics (`STATS\ttotal_docs\tavg_doc_length`) and individual document statistics (`DOC\tdoc_id\tdoc_length`). These statistics are essential for the BM25 scoring function.
    *   **Stage 3 (Cassandra Storage):**
        *   `mapper3.py`: Acts as an identity mapper, simply passing through the outputs from Stage 1 and Stage 2 reducers.
        *   `reducer3.py`: Connects to the Cassandra cluster (`cassandra-server`). It parses the input lines and writes the data into predefined Cassandra tables. This reducer handles the actual persistence of the inverted index and document statistics.

3.  **Data Storage:** Apache Cassandra was selected as the database to store the index and related statistics. Its distributed architecture, scalability, and efficient key-value lookup capabilities make it well-suited for storing large inverted indexes.
    *   **Keyspace:** `search_engine`
    *   **Tables:**
        *   `term_index (term text, doc_id text, term_freq int, positions text, PRIMARY KEY (term, doc_id))`: Stores the core inverted index, mapping terms to the documents they appear in, along with term frequency and positions.
        *   `document_stats (doc_id text PRIMARY KEY, doc_length int)`: Stores the length of each indexed document.
        *   `global_stats (id text PRIMARY KEY, total_docs int, avg_doc_length double)`: Stores corpus-wide statistics (total document count and average document length) under a single key ("global").

4.  **Text Processing:** The Natural Language Toolkit (NLTK) library was used within `mapper1.py` for standard text processing tasks, specifically:
    *   **Tokenization:** Breaking text into words (using a simple regex `\w+`).
    *   **Stopword Removal:** Filtering out common English words that typically don't contribute significantly to search relevance.
    *   **Stemming:** Reducing words to their root form (using Porter Stemmer) to ensure variations of a word are treated as the same term (e.g., "running", "ran" -> "run").

5.  **Orchestration:** The `index.sh` script orchestrates the entire indexing process. It takes an optional input path (defaulting to `/index/data` in HDFS), creates necessary temporary directories in HDFS, and sequentially executes the three Hadoop streaming jobs.

## Demonstration

This section provides instructions on how to run the indexing component and describes the expected outcome.

**Running the Indexing Process:**

1.  **Start Services:** Ensure the Docker environment is running with the Hadoop cluster (master and slave nodes) and Cassandra service active. This is typically done via:
    ```bash
    docker-compose up -d
    ```
2.  **Prepare Data (if necessary):** The sample data (`a.parquet`) needs to be processed into individual text files and placed in HDFS. The provided `prepare_data.sh` script handles this:
    *   Access the master container: `docker exec -it cluster-master bash`
    *   Navigate to the app directory: `cd /app`
    *   Run the preparation script: `./prepare_data.sh`
    This script executes `prepare_data.py` (using PySpark locally) to create text files in `/app/data` and then copies them to `/index/data` in HDFS.
3.  **Run Indexing:** Execute the main indexing script within the `cluster-master` container:
    ```bash
    ./index.sh
    ```
    (Optional: Provide a specific HDFS path or local file path as an argument: `./index.sh /path/to/your/data`)

4.  **Monitor Execution:** The script will print progress messages indicating which MapReduce job is running. Hadoop's job tracker UI (accessible via the master node's web UI, typically port 8088) can be used for detailed monitoring.

**Expected Outcome & Verification:**

Upon successful completion of `index.sh`:

1.  Three MapReduce jobs will have run sequentially.
2.  The script will print "Indexing completed. Check Cassandra for the index data."
3.  The index data (inverted index, document stats, global stats) will be populated in the `search_engine` keyspace within the Cassandra database. You can verify this using `cqlsh` inside the `cassandra-server` container or by inspecting the output logs from `reducer3.py` which print messages upon successful insertion.


**Note on Querying:**

Due to time constraints, the implementation and demonstration of the search query component (`query.py` and `search.sh`), which would utilize the indexed data and the BM25 algorithm in PySpark, were not completed. The focus remained on establishing the robust MapReduce-based indexing pipeline into Cassandra.
