from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings
from app.models.chunk import Chunk
from app.models.document import Document


class EmbeddingService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for document processing")
        if not settings.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is required for document processing")

        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.pinecone = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self._ensure_index()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.openai_client.embeddings.create(model=settings.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def upsert_chunks(self, document: Document, chunks: list[Chunk]) -> None:
        embeddings = self.embed_texts([chunk.content for chunk in chunks])
        vectors = []
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            embedding_id = f"document:{document.id}:chunk:{chunk.chunk_index}"
            chunk.embedding_id = embedding_id
            vectors.append(
                {
                    "id": embedding_id,
                    "values": embedding,
                    "metadata": {
                        "document_id": document.id,
                        "user_id": document.user_id,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "source_type": chunk.source_type,
                        "filename": document.original_filename,
                        "text": chunk.content,
                    },
                }
            )

        if vectors:
            self.index.upsert(vectors=vectors, namespace=settings.pinecone_namespace)

    def query(self, text: str, user_id: str, top_k: int = 8) -> list[dict[str, object]]:
        embedding = self.embed_texts([text])[0]
        response = self.index.query(
            vector=embedding,
            top_k=top_k,
            namespace=settings.pinecone_namespace,
            include_metadata=True,
            filter={"user_id": {"$eq": user_id}},
        )
        return list(response.get("matches", []))

    def _ensure_index(self):
        indexes = self.pinecone.list_indexes()
        if hasattr(indexes, "names"):
            existing = set(indexes.names())
        else:
            existing = {index["name"] for index in indexes}
        if settings.pinecone_index_name not in existing:
            self.pinecone.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.pinecone_embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
            )
        return self.pinecone.Index(settings.pinecone_index_name)
