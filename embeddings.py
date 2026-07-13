from FlagEmbedding import BGEM3FlagModel
import config


class BGEM3Embedder:
    def __init__(self, model_name=config.BGE_M3_MODEL_NAME, use_fp16=True):
        self.model = BGEM3FlagModel(model_name, use_fp16=use_fp16)

    def encode_documents(self, texts, batch_size=12):
        output = self.model.encode(
            texts,
            batch_size=batch_size,
            max_length=8192,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        return output["dense_vecs"], output["lexical_weights"]

    def encode_query(self, text):
        output = self.model.encode(
            [text],
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        return output["dense_vecs"][0], output["lexical_weights"][0]


def to_milvus_sparse(lexical_weight):
    return {int(k): float(v) for k, v in lexical_weight.items()}
