from FlagEmbedding import FlagReranker
import config


class CrossEncoderReranker:
    def __init__(self, model_name=config.RERANKER_MODEL_NAME, use_fp16=True):
        self.model = FlagReranker(model_name, use_fp16=use_fp16)

    def rerank(self, query, candidates, top_k=config.TOP_K_RERANK):
        if not candidates:
            return []

        pairs = [(query, c["chunk_text"]) for c in candidates]
        scores = self.model.compute_score(pairs, normalize=True)

        if isinstance(scores, float):
            scores = [scores]

        for c, s in zip(candidates, scores):
            c["rerank_score"] = s

        candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
        return candidates[:top_k]
