from app.services.retrieval_service import RetrievalService


def test_rrf_combines_ranked_lists() -> None:
    service = RetrievalService.__new__(RetrievalService)

    scores = service._reciprocal_rank_fusion([["a", "b"], ["b", "c"]])

    assert scores["b"] > scores["a"]
    assert scores["b"] > scores["c"]
