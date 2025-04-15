#!/bin/bash
echo "This script includes commands to run mapreduce jobs using hadoop streaming to index documents"

# Get input path (default is /index/data)
INPUT_PATH=${1:-"/index/data"}
echo "Input path is: $INPUT_PATH"

if [ -e "$INPUT_PATH" ]; then
    echo "Input path '$INPUT_PATH' exists locally. Copying to HDFS."
    HDFS_TMP_INPUT="/tmp/index/input_local"
    hdfs dfs -rm -r -f $HDFS_TMP_INPUT
    hdfs dfs -put $INPUT_PATH $HDFS_TMP_INPUT
    HDFS_INPUT_PATH=$HDFS_TMP_INPUT
else
    echo "Input path '$INPUT_PATH' assumed to be on HDFS."
    HDFS_INPUT_PATH=$INPUT_PATH
fi

# Create necessary HDFS directories
hdfs dfs -mkdir -p /tmp/index/output1
hdfs dfs -mkdir -p /tmp/index/output2
hdfs dfs -mkdir -p /tmp/index/output3

hdfs dfs -rm -r -f /tmp/index/output1
hdfs dfs -rm -r -f /tmp/index/output2
hdfs dfs -rm -r -f /tmp/index/output3

# Step 1: Extract terms and positions from documents
echo "Running MapReduce Job 1: Extracting terms and positions"
hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar \
    -files /app/mapreduce/mapper1.py,/app/mapreduce/reducer1.py \
    -mapper "python3 mapper1.py" \
    -reducer "python3 reducer1.py" \
    -input $HDFS_INPUT_PATH \
    -output /tmp/index/output1

# Step 2: Calculate document statistics for BM25
echo "Running MapReduce Job 2: Calculating document statistics"
hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar \
    -files /app/mapreduce/mapper2.py,/app/mapreduce/reducer2.py \
    -mapper "python3 mapper2.py" \
    -reducer "python3 reducer2.py" \
    -input $HDFS_INPUT_PATH \
    -output /tmp/index/output2

# Step 3: Store index data in Cassandra
echo "Running MapReduce Job 3: Storing index in Cassandra"
hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar \
    -files /app/mapreduce/mapper3.py,/app/mapreduce/reducer3.py \
    -mapper "python3 mapper3.py" \
    -reducer "python3 reducer3.py" \
    -input /tmp/index/output1/part-*,/tmp/index/output2/part-* \
    -output /tmp/index/output3

echo "Indexing completed. Check Cassandra for the index data."
