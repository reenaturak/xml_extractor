# XML Extractor

A small Python utility to extract `<doc-number>` values.
It prioritizes `epo` format documents first, followed by `patent-office` ones.


## 🔧 Installation and Run

1. Clone the repository -  git clone https://github.com/reenaturak/xml_extractor.git
2. cd xml_extractor
3. uv sync
4. Run - uv run python -m xml_package.extractor

# Assumptions

1. File type is .xml, .txt, .data, .zip, .html
2. File contains valid xml contents, encoding = utf-8
3. The XML has a single root element
4. There can be multiple application-reference
5. Every <document-id> element contains exactly one <doc-number> child element
6. document-id elements may have a format attribute and/or a load-source attribute; either can indicate source type.
7. Format is consistently spelled as "docdb" and "original"
8. Tags may have XML namespaces

To do's for real scenario
1. Set default value for doc-number if its empty or not found, before storing it or passing to downstream
2. Validate for unacceptable or corrupt values like special characters, alphanumeric, etc
3. Validate for the length of the doc-number

