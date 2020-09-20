# Near Duplicate Video Retrieval

We have witnessed an explosive growth of video data in a variety of video sharing websites with billions of videos being available on the internet,
it becomes a major challenge to perform near-duplicate video retrieval (NDVR) from a large-scale video database. NDVR aims to retrieve the near-duplicate
videos from a massive video database, where near-duplicate videos are defined as videos that are visually close to the original videos.

Users have a strong incentive to copy a trending short video & upload an augmented version to gain attention. With the growth of short videos, new
difficulties and challenges for detecting near duplicate short videos appears.

Here, we have built a Neural Search solution using Jina to solve the challenge of NDVR.


**Table of Contents**

- [Near Duplicate Video Retrieval](#near-duplicate-video-retrieval)
  - [How does it look like?](#how-does-it-look-like)
  - [Challenges](#challenges)
  - [Prerequirements](#prerequirements)
    - [Download the data](#download-the-data)
  - [Run Index Flow](#run-index-flow)
  - [Run Query Flow](#run-query-flow)

## How does it look like?

![Example](./images/ndvr-2.png)

Example of hard positive candidate videos.
Top row: side morrored, color-filtered, and waterwashed.
Middle row: horizontal screen changed to vertical screen with large black margins.
Botton row: rotated

## Challenges

![Challenge](./images/ndvr-3.png)

Example of hard negative videos. All the candidates are
visually similar to the query but not near-duplicates.

## Prerequirements

```bash
pip install --upgrade -r requirements.txt
```

### Download the data



## Run Index Flow

```bash
python app.py index
```

The index Flow is defined as follows:
```yaml
!Flow
with:
  logserver: true
pods:
  chunk_seg:
    uses: craft/index-craft.yml
    parallel: $PARALLEL
    read_only: true
  doc_idx:
    uses: index/doc.yml
  tf_encode:
    uses: encode/encode.yml
    needs: chunk_seg
    parallel: $PARALLEL
    read_only: true
  chunk_idx:
    uses: index/chunk.yml
    shards: $SHARDS
    separated_workspace: true
  join_all:
    uses: _merge
    needs: [doc_idx, chunk_idx]
    read_only: true
```

This breaks down into the following steps:
1. Segment each video into chunks;
2. Encode each chunk as a fixed-length vector;
3. Store all vector representations in a vector database with *shards*.


## Run Query Flow

```bash
python app.py search
```

You can then open [Jinabox](https://jina.ai/jinabox.js/) with the custom endpoint `http://localhost:45678/api/search`

The query Flow is defined as follows:

```yaml
!Flow
with:
  logserver: true
  read_only: true  # better add this in the query time
pods:
  chunk_seg:
    uses: craft/index-craft.yml
    parallel: $PARALLEL
  tf_encode:
    uses: encode/encode.yml
    parallel: $PARALLEL
  chunk_idx:
    uses: index/chunk.yml
    shards: $SHARDS
    separated_workspace: true
    polling: all
    uses_reducing: _merge_all
    timeout_ready: 100000 # larger timeout as in query time will read all the data
  ranker:
    uses: BiMatchRanker
  doc_idx:
    uses: index/doc.yml
```


The query flow breaks down into the following steps:
1. Do steps 1,2 in the index flow for each incoming query;
2. Retrieve relevant chunks from database;
3. Aggregate the chunk-level score back to document-level;
4. Return the top-k results to users.

