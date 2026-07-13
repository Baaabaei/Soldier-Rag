from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    AnnSearchRequest,
    RRFRanker,
)
import config

FIELDS = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="question_title", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=4000),
    FieldSchema(name="full_context", dtype=DataType.VARCHAR, max_length=8000),
    FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=config.DENSE_DIM),
    FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
]


def connect():
    connections.connect(uri=config.MILVUS_URI)


def get_or_create_collection():
    connect()

    if utility.has_collection(config.COLLECTION_NAME):
        return Collection(config.COLLECTION_NAME)

    schema = CollectionSchema(FIELDS, description="Dadrah sarbazi QA hybrid RAG")
    collection = Collection(config.COLLECTION_NAME, schema)

    collection.create_index(
        field_name="dense_vector",
        index_params={
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {"M": 16, "efConstruction": 200},
        },
    )
    collection.create_index(
        field_name="sparse_vector",
        index_params={"index_type": "SPARSE_INVERTED_INDEX", "metric_type": "IP"},
    )

    return collection


def insert_records(collection, records):
    collection.insert(records)
    collection.flush()


def hybrid_search(collection, dense_query, sparse_query, top_k=config.TOP_K_RETRIEVE):
    collection.load()

    dense_req = AnnSearchRequest(
        data=[dense_query.tolist() if hasattr(dense_query, "tolist") else dense_query],
        anns_field="dense_vector",
        param={"metric_type": "COSINE", "params": {"ef": 64}},
        limit=top_k,
    )
    sparse_req = AnnSearchRequest(
        data=[sparse_query],
        anns_field="sparse_vector",
        param={"metric_type": "IP"},
        limit=top_k,
    )

    ranker = RRFRanker()

    results = collection.hybrid_search(
        reqs=[dense_req, sparse_req],
        rerank=ranker,
        limit=top_k,
        output_fields=["url", "question_title", "chunk_text", "full_context", "tags"],
    )

    return results[0]
