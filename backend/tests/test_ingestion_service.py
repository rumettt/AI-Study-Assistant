from app.services.ingestion_service import IngestionService, ParsedBlock


def test_chunk_blocks_respects_content_order() -> None:
    service = IngestionService.__new__(IngestionService)
    blocks = [
        ParsedBlock(text="Heading\nFirst concept paragraph.", page_number=1, source_type="pdf"),
        ParsedBlock(text="Second concept paragraph.", page_number=2, source_type="pdf"),
    ]

    chunks = service.chunk_blocks(blocks)

    assert chunks
    assert "First concept" in chunks[0].content
    assert chunks[0].chunk_index == 0
    assert chunks[0].source_type == "pdf"
