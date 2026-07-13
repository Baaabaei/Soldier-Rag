from anthropic import Anthropic
import config
from embeddings import BGEM3Embedder, to_milvus_sparse
from vector_store import get_or_create_collection, hybrid_search
from reranker import CrossEncoderReranker
from memory import ConversationMemory

SYSTEM_PROMPT = (
    "شما یک دستیار حقوقی هستید که فقط بر اساس منابع بازیابی‌شده از سوالات و پاسخ‌های حقوقی سایت دادراه "
    "درباره سربازی پاسخ می‌دهید. اگر پاسخ در منابع نبود، صریحاً بگویید اطلاعات کافی در منابع موجود نیست "
    "و پیشنهاد بدهید کاربر با یک وکیل مشورت کند. همیشه در پایان پاسخ، لینک منابع استفاده‌شده را ذکر کنید."
)


class RAGPipeline:
    def __init__(self):
        self.embedder = BGEM3Embedder()
        self.collection = get_or_create_collection()
        self.reranker = CrossEncoderReranker()
        self.memory = ConversationMemory()
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def build_context(self, ranked_results):
        blocks = [f"[منبع: {r['url']}]\n{r['full_context']}" for r in ranked_results]
        return "\n\n---\n\n".join(blocks)

    def answer(self, session_id, user_query):
        standalone_query = self.memory.contextualize_query(session_id, user_query)

        dense_query, sparse_query_raw = self.embedder.encode_query(standalone_query)
        sparse_query = to_milvus_sparse(sparse_query_raw)

        hits = hybrid_search(self.collection, dense_query, sparse_query)

        candidates = [
            {
                "url": hit.entity.get("url"),
                "question_title": hit.entity.get("question_title"),
                "chunk_text": hit.entity.get("chunk_text"),
                "full_context": hit.entity.get("full_context"),
                "tags": hit.entity.get("tags"),
            }
            for hit in hits
        ]

        top_results = self.reranker.rerank(standalone_query, candidates)
        context = self.build_context(top_results)

        user_message = f"منابع بازیابی‌شده:\n{context}\n\nسوال کاربر: {user_query}"

        response = self.client.messages.create(
            model=config.GENERATION_MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        answer_text = response.content[0].text

        self.memory.add_turn(session_id, "user", user_query)
        self.memory.add_turn(session_id, "assistant", answer_text)

        sources = list(dict.fromkeys(r["url"] for r in top_results))
        return answer_text, sources
