import json
import sys
import config
from embeddings import BGEM3Embedder, to_milvus_sparse
from vector_store import get_or_create_collection, insert_records


def chunk_text(text, max_chars=config.CHUNK_MAX_CHARS, overlap=config.CHUNK_OVERLAP_CHARS):
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap

    return chunks


def build_records(data):
    records = []

    for item in data:
        answers_text = "\n".join(
            f"{a['lawyer_name']} ({a['lawyer_city']}): {a['answer_text']}"
            for a in item.get("answers", [])
        )

        full_context = (
            f"عنوان: {item['question_title']}\n"
            f"سوال: {item['question_text']}\n"
            f"پاسخ‌ها:\n{answers_text}"
        )[:8000]

        tags_str = ", ".join(item.get("tags", []))
        searchable_text = f"{item['question_title']}\n{item['question_text']}"

        for chunk in chunk_text(searchable_text):
            records.append({
                "url": item["url"],
                "question_title": item["question_title"],
                "chunk_text": chunk,
                "full_context": full_context,
                "tags": tags_str,
            })

    return records


def main(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = build_records(data)
    print(f"تعداد رکوردهای ساخته‌شده: {len(records)}")

    embedder = BGEM3Embedder()
    texts = [r["chunk_text"] for r in records]

    dense_vecs, lexical_weights = embedder.encode_documents(texts)

    for r, dense, sparse in zip(records, dense_vecs, lexical_weights):
        r["dense_vector"] = dense.tolist()
        r["sparse_vector"] = to_milvus_sparse(sparse)

    collection = get_or_create_collection()
    insert_records(collection, records)

    print("درج در Milvus کامل شد.")



if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/dadrah_sarbazi_qa.json")
