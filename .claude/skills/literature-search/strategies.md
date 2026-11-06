# Literature Review Strategies

## Search Strategies

### Snowball Search

Start with a known relevant paper, then expand:

1. **Backward snowballing** — Check the paper's references
2. **Forward snowballing** — Find papers that cite it (use "Cited by" in Google Scholar or Semantic Scholar)

Best for: Building comprehensive coverage from a starting point.

### Systematic Search

Structured approach for thorough coverage:

1. Define search terms and synonyms
2. Search each database systematically
3. Apply inclusion/exclusion criteria
4. Document the process (for reproducibility)

Best for: Review papers, grant proposals, thesis literature reviews.

### Exploratory Search

When entering a new field:

1. Start broad: `"<topic>" review OR survey`
2. Identify key authors and labs
3. Find seminal papers (high citations, frequently referenced)
4. Narrow to specific subtopics

Best for: Learning a new research area.

---

## Finding Key Papers

### Seminal Works

Papers that established a field or introduced key concepts:

- High citation count (thousands)
- Referenced in most papers on the topic
- Often older (5-20+ years)

Search: `"<topic>" seminal OR foundational OR "first proposed"`

### Recent Advances

Current state of the art:

- Published in last 2-3 years
- Moderate but growing citations
- Presented at top venues

Search: `"<topic>" 2023..2025` or use date filters

### Survey Papers

Comprehensive overviews that synthesize a field:

Search: `"<topic>" survey OR review OR "systematic review" OR overview`

---

## Evaluating Sources

### Quality Indicators

| Indicator | What it means |
|-----------|---------------|
| High citations | Influential (but check age) |
| Top venue | Peer-reviewed, competitive |
| Author reputation | Check h-index, affiliations |
| Reproducibility | Code/data available |
| Recent updates | Active research area |

### Peer Review Status

- **Journal articles** — Peer-reviewed
- **Conference papers** — Usually peer-reviewed
- **arXiv/preprints** — Not peer-reviewed (verify claims carefully)
- **Technical reports** — Varies

### Red Flags

- Predatory journals (check journal reputation)
- Unreproducible claims
- Retracted papers (check Retraction Watch)
- Excessive self-citation

---

## Organizing Results

### Categorization Schemes

By **topic/subtopic**:
```
Machine Learning for Chemistry
├── Molecular Property Prediction
├── Reaction Prediction
├── Molecular Generation
└── Force Fields / Potentials
```

By **methodology**:
```
├── Graph Neural Networks
├── Transformers
├── Diffusion Models
└── Traditional ML
```

By **chronology**:
```
├── Foundational (pre-2015)
├── Deep Learning Era (2015-2020)
└── Foundation Models (2020-present)
```

### Reading Prioritization

1. **Must read** — Seminal works, directly relevant
2. **Should read** — Related methods, key comparisons
3. **Skim** — Background, tangentially related
4. **Reference only** — Cite but don't read fully

---

## Search Refinement

### Narrowing Results

Add specificity:
- Specific methods: `"graph neural network" NOT "convolutional"`
- Specific domains: `"drug discovery" AND "virtual screening"`
- Exclude terms: `-review -survey` (for original research only)

### Broadening Results

- Use synonyms: `"molecular property" OR "chemical property"`
- Remove constraints: Drop year filters
- Try related terms: Check MeSH terms, keywords from relevant papers

### Query Templates

**Finding methods applied to a domain:**
```
"<method>" AND "<domain>" AND ("<task1>" OR "<task2>")
```

**Finding comparisons:**
```
"<method1>" AND "<method2>" comparison OR benchmark
```

**Finding implementations:**
```
"<method>" code OR implementation OR github
```

---

## Documentation

### For Reproducibility

Track your search process:

```markdown
## Search Log

### Date: 2024-03-15

**Query:** site:arxiv.org "graph neural network" "molecular property"
**Database:** arXiv via Google
**Results:** 47 papers
**Relevant:** 12 papers added to bibliography

**Query:** site:pubmed.ncbi.nlm.nih.gov "machine learning" "drug discovery" review
**Database:** PubMed
**Results:** 234 papers
**Relevant:** 8 review articles
```

### Annotation

For each paper, note:

- **Key contribution**: What's new?
- **Methods**: What approach?
- **Relevance**: How does it relate to your work?
- **Limitations**: What's missing?
- **Follow-up**: Papers to read next?

---

## Tools

### Reference Management

- **Zotero** — Free, open source, browser extension
- **Mendeley** — Free, PDF annotation
- **Paperpile** — Google Docs integration
- **EndNote** — Institutional standard

### Discovery Tools

- **Connected Papers** — Visual citation graphs
- **Research Rabbit** — Paper recommendations
- **Semantic Scholar** — AI-powered recommendations
- **Litmaps** — Interactive literature maps

### Alerting

- **Google Scholar Alerts** — Email for new papers matching query
- **arXiv alerts** — Subscribe to categories
- **Semantic Scholar Alerts** — Follow authors or topics

---

## Programmatic Access with arXiv API

For large-scale or automated literature reviews, use the arXiv API:

### Official API (Atom 1.0)

```
http://export.arxiv.org/api/query
```

**Rate limits:**
- 1 request every 3 seconds
- Single connection at a time

**Example query:**
```bash
curl "http://export.arxiv.org/api/query?search_query=all:machine+learning&start=0&max_results=50"
```

### OAI-PMH Interface

For bulk metadata harvesting with date-based updates:
```
https://oaipmh.arxiv.org/oai
```

### RSS/ATOM Feeds

For tracking new papers by category:
```
https://rss.arxiv.org/rss/{category}
```

### Getting Full Text

The arXiv API returns metadata only. For full text:

1. **HTML (machine-readable)**: `https://arxiv.org/html/{id}`
2. **PDF**: `https://arxiv.org/pdf/{id}.pdf` (requires OCR for text)
3. **LaTeX source**: Via S3 bulk data (`s3://arxiv/`) - requires unzipping

### Recommended Workflow for Paper Reading

1. **Spawn a subagent per paper** for independent processing
2. **Verify relevance**: Fetch title and abstract via API
3. **Fetch full text**: Use HTML endpoint when available
4. **Extract references**: Store reference list separately
5. **Perform tasks**: Summarize, extract citations, analyze

See [databases.md](databases.md#the-arxiv-api) for complete API details.
