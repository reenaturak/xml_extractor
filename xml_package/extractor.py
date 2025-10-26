import xml.etree.ElementTree as ET
import zipfile
import os
import logging
from dataclasses import dataclass
from typing import Optional, List, Iterable, Set

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class Document:
    doc_number: Optional[str]
    format: Optional[str] = None
    load_source: Optional[str] = None
    country: Optional[str] = None


def _local_name(tag: str) -> str:
    """Return the local-name of an ElementTree tag (strip namespace)."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _iter_document_id_elements(root: ET.Element) -> Iterable[ET.Element]:
    """
    Yield elements whose local-name is 'document-id', regardless of namespace.
    """
    for elem in root.iter():
        if _local_name(elem.tag) == "document-id":
            yield elem


def _find_child_by_local_name(parent: ET.Element, local_name: str) -> Optional[ET.Element]:
    """Find first child of parent whose local-name matches `local_name`."""
    for c in parent:
        if _local_name(c.tag) == local_name:
            return c
    return None


def _parse_xml_string(xml_content: str) -> ET.Element:
    try:
        return ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"XML parse error: {e}")


def extract_doc_numbers_from_file(file_path: str) -> List[str]:
    """
    Extracts <doc-number> values from XML or ZIP files and returns them
    in priority order: 'epo' first, then 'patent-office'.
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")

    xml_strings: List[str] = []

    # Read file(s)
    try:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, "r") as z:
                xml_files = [n for n in z.namelist() if n.lower().endswith(".xml")]
                if not xml_files:
                    raise ValueError("No XML files found in ZIP archive.")
                # read all xml files
                for name in xml_files:
                    with z.open(name) as f:
                        # decode with utf-8 but ignore errors
                        content = f.read().decode("utf-8", errors="ignore")
                        xml_strings.append(content)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                xml_strings.append(f.read())
    except Exception as e:
        raise ValueError(f"Error reading file '{file_path}': {e}")

    # containers for priority buckets
    epo_docs: List[str] = []
    patent_office_docs: List[str] = []
    other_docs: List[str] = []
    seen: Set[str] = set()

    # Helper for classification
    def classify_and_append(doc_elem: ET.Element, doc_number: str):
        fmt = (doc_elem.get("format") or "").strip().lower()
        load_source = (doc_elem.get("load-source") or "").strip().lower()

        # classify: epo first, then patent-office
        is_epo = fmt == "epo" or load_source in {"docdb"}
        is_patent_office = load_source == "patent-office" or fmt == "original"

        if is_epo:
            target = epo_docs
        elif is_patent_office:
            target = patent_office_docs
        else:
            target = other_docs

        if doc_number not in seen:
            seen.add(doc_number)
            target.append(doc_number)

    # Parse each XML string
    for xml_content in xml_strings:
        root = _parse_xml_string(xml_content)

        for doc_id in _iter_document_id_elements(root):
            # find doc-number child robustly (namespace-agnostic)
            doc_number_elem = _find_child_by_local_name(doc_id, "doc-number")

            doc_number = None
            if doc_number_elem is not None and doc_number_elem.text and doc_number_elem.text.strip():
                doc_number = doc_number_elem.text.strip()
            else:
                logger.warning(
                    "Missing or empty <doc-number> under document-id. Attributes: %s",
                    {k: doc_id.get(k) for k in ("format", "load-source")}
                )
                continue

            # append to appropriate bucket
            classify_and_append(doc_id, doc_number)

    # Return epo first, then patent-office, then others (if any)
    return epo_docs + patent_office_docs + other_docs

print(extract_doc_numbers_from_file("data/test.txt"))
