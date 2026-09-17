from sentence_transformers import SentenceTransformer

class Embedder:
    _model_instance = None

    def _load_model(self):
        if Embedder._model_instance is None:
            print("正在加载向量模型......",flush=True)

            Embedder._model_instance = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
            )

        return Embedder._model_instance

    def encode(self, text):
        model = self._load_model()

        vector = model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.tolist()

if __name__ == "__main__":
    embedder = Embedder()

    vector = embedder.encode("Python列表可以添加和删除元素。")
    print("第一次向量维度：", len(vector))

    vector = embedder.encode("如何修改Python列表？")
    print("第二次向量维度：", len(vector))
