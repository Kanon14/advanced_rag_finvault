from backend.ingestion.parsers.base import ParserAdapter
from backend.ingestion.parsers.docling_parser import DoclingParser
from backend.ingestion.parsers.pypdf_parser import PyPdfParser


def build_parser() -> ParserAdapter:
    docling_parser = DoclingParser()
    if docling_parser.is_available:
        return docling_parser
    return PyPdfParser()
