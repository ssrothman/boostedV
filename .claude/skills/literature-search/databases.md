# Scientific Database Reference

## arXiv

Preprint server for physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, and economics.

### Search Syntax

```
site:arxiv.org "<exact phrase>"
site:arxiv.org author:"LastName"
site:arxiv.org cs.LG "<machine learning topic>"
site:arxiv.org 2024 "<recent work>"
```

### Category Codes

| Code | Field |
|------|-------|
| `cs.LG` | Machine Learning |
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `physics.comp-ph` | Computational Physics |
| `cond-mat` | Condensed Matter |
| `quant-ph` | Quantum Physics |
| `astro-ph` | Astrophysics |
| `math.NA` | Numerical Analysis |
| `stat.ML` | Machine Learning (Statistics) |
| `q-bio` | Quantitative Biology |

### arXiv IDs

Format: `YYMM.NNNNN` (e.g., `2301.07041`) or legacy format (e.g., `hep-th/9901001`)

Direct URL: `https://arxiv.org/abs/2301.07041`
PDF: `https://arxiv.org/pdf/2301.07041.pdf`

### The arXiv API

arXiv provides several endpoints for programmatic access. The **official arXiv API** (Atom 1.0-based) is the primary interface for metadata queries.

#### Official API Endpoint

```
http://export.arxiv.org/api/query
```

**Query Examples:**

```bash
# Search for papers with "electron" in title/abstract
curl "http://export.arxiv.org/api/query?search_query=all:electron"

# Get specific papers by ID
curl "http://export.arxiv.org/api/query?id_list=hep-th/9901001"

# With paging and sorting
curl "http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=10&sortBy=lastUpdatedDate&sortOrder=descending"
```

#### Response Format

Returns Atom XML feed with `<entry>` elements containing:
- `<title>`, `<summary>` (abstract), `<id>`
- `<author>` elements with `<name>`
- `<link rel="alternate">` - abstract page
- `<link rel="related" title="pdf">` - PDF download link
- `<arxiv:comment>`, `<arxiv:journal_ref>`, `<arxiv:doi>`
- `<category>` elements for subject classification

#### Rate Limits

- Maximum **1 request every 3 seconds**
- **Single connection at a time** (no parallel requests)
- Exceeding limits may result in blocked access

#### Endpoints Summary

| Endpoint | URL Pattern | Purpose |
|----------|-------------|---------|
| API Query | `http://export.arxiv.org/api/query` | Metadata in Atom XML format |
| abs | `https://arxiv.org/abs/{id}` | HTML abstract page (human-readable) |
| pdf | `https://arxiv.org/pdf/{id}.pdf` | PDF download (not machine-readable) |
| html | `https://arxiv.org/html/{id}` | HTML source (when available, machine-readable) |
| latex source | via S3 bulk download | TeX/LaTeX source files (requires unzip) |

#### OAI-PMH Interface

For bulk metadata harvesting:
```
https://oaipmh.arxiv.org/oai
```
Supports: `Identify`, `ListRecords`, `GetRecord`, `ListSets`

#### RSS/ATOM Feeds

For tracking new papers by category:
```
https://rss.arxiv.org/rss/{category}
```
Examples: `hep-th`, `cs.LG`, `physics.gen-ph`

### Python Libraries for arXiv Access

Several Python libraries simplify arXiv API access:

#### arxiv (official community library)

```python
import arxiv

# Search for papers
client = arxiv.Client()
search = arxiv.Search(
    query="all:machine learning",
    max_results=10,
    sort_by=arxiv.SortCriterion.LastUpdatedDate
)

for result in client.results(search):
    print(f"Title: {result.title}")
    print(f"Abstract: {result.summary}")
    print(f"PDF: {result.pdf_url}")
```

#### pycrossref (for DOI resolution)

```python
import crossref

# Get DOI for an arXiv paper
result = crossref.works(query="electron quantum mechanics")
print(result['DOI'])
```

#### General purpose (requests + xml)

```python
import requests
import xml.etree.ElementTree as ET

# Query arXiv API directly
url = "http://export.arxiv.org/api/query"
params = {
    "search_query": "all:electron",
    "start": 0,
    "max_results": 10
}

response = requests.get(url, params=params)
root = ET.fromstring(response.content)

# Parse results
for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
    title = entry.find('{http://www.w3.org/2005/Atom}title').text
    abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text
    print(f"{title}\n{abstract}\n")
```

### Getting Full Text

The arXiv API **does not return full text** directly. For full text access:

1. **For metadata only**: Use the official API (above)
2. **For HTML content**: Use `https://arxiv.org/html/{id}` (experimental, machine-readable)
3. **For PDF**: Use `https://arxiv.org/pdf/{id}.pdf` (not machine-readable)
4. **For source LaTeX**: Access via S3 bulk data (requester-pays bucket `s3://arxiv/`)

#### arXiv Bulk Data (S3)

For large-scale access to full papers:
- **Bucket**: `s3://arxiv/` (requester-pays)
- **PDFs**: ~2.7 TB in tar files (e.g., `pdf/arXiv_pdf_1001_001.tar`)
- **Source files**: ~2.9 TB of TeX/LaTeX in tar.gz format
- **Update frequency**: Monthly for new content

### Extracting Reference Lists

Reference lists are **not directly available** through the arXiv API. To get references:

1. Use the API to get paper metadata and PDF link
2. Download the PDF from `https://arxiv.org/pdf/{id}.pdf`
3. Parse references from the PDF (requires OCR or specialized tools)
4. Alternatively, use Semantic Scholar's API which provides reference data

### Notes

- Preprints are not peer-reviewed
- Many papers have published versions — look for DOI links
- Check version history (`v1`, `v2`, etc.) for updates
- arXiv does **not** allow storing and serving PDFs from your servers (copyright restrictions)
- Acknowledge arXiv: "Thank you to arXiv for use of its open access interoperability"
- Review the [Terms of Use for arXiv APIs](https://info.arxiv.org/help/api/tou.html)

---

## PubMed

Biomedical and life sciences literature from MEDLINE, life science journals, and online books.

### Search Syntax

```
site:pubmed.ncbi.nlm.nih.gov "<topic>"
site:pubmed.ncbi.nlm.nih.gov "<gene name>" review
site:pubmed.ncbi.nlm.nih.gov "<disease>" clinical trial
```

### PubMed Advanced Search

For complex queries, use PubMed directly:

- `[Title/Abstract]` — Search title and abstract
- `[Author]` — Author name
- `[Journal]` — Journal name
- `[MeSH Terms]` — Medical Subject Headings

Example: `"machine learning"[Title/Abstract] AND "drug discovery"[Title/Abstract]`

### PMIDs

PubMed IDs are numeric (e.g., `34567890`)

Direct URL: `https://pubmed.ncbi.nlm.nih.gov/34567890/`

### Notes

- All indexed articles are peer-reviewed
- PMC (PubMed Central) provides free full text for some articles
- Use MeSH terms for precise medical/biological searches

---

## Semantic Scholar

AI-powered academic search with citation analysis and paper recommendations.

### Search Syntax

```
site:semanticscholar.org "<topic>"
site:semanticscholar.org author:"<name>"
```

### Features

- **Citation counts** — Useful for identifying influential papers
- **Influential citations** — Distinguishes significant from peripheral citations
- **TLDR** — AI-generated paper summaries
- **Related papers** — Algorithmic recommendations
- **Citation graphs** — Visualize citation networks

### Semantic Scholar API

For programmatic access:

```bash
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=machine+learning&limit=10"
```

### Corpus IDs

Semantic Scholar uses Corpus IDs and supports DOIs, arXiv IDs, and PMIDs.

---

## Google Scholar

Broad coverage across disciplines, including books, theses, and conference papers.

### Search Syntax

```
"<exact phrase>"
author:"<name>"
intitle:"<word in title>"
source:"<journal name>"
```

### Date Filtering

- Click "Since Year" in sidebar
- Or add to query: `"topic" 2023..2025`

### Features

- **Cited by** — Find papers citing a given work
- **Related articles** — Similar papers
- **Versions** — Find different versions (preprint, published)
- **Create alert** — Email notifications for new papers

### Notes

- Broadest coverage but noisiest results
- Citation counts may differ from other sources
- No API access — use web search

---

## Specialized Databases

### ChemRxiv / ACS Publications

Chemistry preprints and published work.

```
site:chemrxiv.org "<chemistry topic>"
site:pubs.acs.org "<chemistry topic>"
```

### IEEE Xplore

Electrical engineering, computer science, electronics.

```
site:ieeexplore.ieee.org "<topic>"
```

### Nature / Science

High-impact general science.

```
site:nature.com "<topic>"
site:science.org "<topic>"
```

### bioRxiv / medRxiv

Biology and medicine preprints.

```
site:biorxiv.org "<topic>"
site:medrxiv.org "<topic>"
```

---

## Choosing a Database

| Research Area | Primary | Secondary |
|--------------|---------|-----------|
| Machine Learning | arXiv (cs.LG) | Semantic Scholar |
| Biomedicine | PubMed | Google Scholar |
| Physics | arXiv | Google Scholar |
| Chemistry | ACS, ChemRxiv | Semantic Scholar |
| Engineering | IEEE Xplore | Google Scholar |
| Cross-disciplinary | Semantic Scholar | Google Scholar |
| Finding citations | Semantic Scholar | Google Scholar |
