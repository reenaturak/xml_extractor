# XML Extractor

A small Python utility to extract `<doc-number>` values.
It prioritizes `epo` format documents first, followed by `patent-office` ones.


## 🔧 Installation

Clone the repository and install dependencies using **uv** or pip:

uv pip install -e 


# Assumptions
1. File type is .xml, .txt, .data, .zip, .html
2. File contains valid xml contents, encoding = utf-8
3. There can be multiple application-reference
4. Every <document-id> element contains exactly one <doc-number> child element
7. document-id elements may have a format attribute and/or a load-source attribute; either can indicate source type.
8. Format is consistently spelled as "docdb" and "original"

To do's for real scenario
1. Set default value for doc-number if its empty or not found, before storing it or passing to downstream
2. Validate for unacceptable or corrupt values like special characters, alphanumeric, etc
3. Validate for the length of the doc-number

