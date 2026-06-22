"""
rag.py — lightweight retrieval over the knowledge/ docs (the RWTH CLAIX
documentation the user provided). Pure standard library: builds a TF-IDF index
over markdown chunks and returns the most relevant chunks for a query.

Why lexical (TF-IDF) and not embeddings: Groq has no embeddings endpoint, and
this must run inside a Vercel serverless function with no vector DB. TF-IDF over
a small, curated doc set is fast, dependency-free, and grounds answers on the
actual documentation instead of the model's memory.
"""

import glob
import math
import os
import re
from collections import Counter

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
_WORD = re.compile(r"[a-z0-9]+")


def _tokenize(text):
    return _WORD.findall(text.lower())


def _chunk(text):
    """Split a markdown doc into chunks on H2 (##) headings; keep small docs whole."""
    parts = re.split(r"\n(?=##\s)", text)
    return [p.strip() for p in parts if p.strip()]


class _Index:
    def __init__(self):
        self.chunks = []      # list of {source, text, tokens(Counter)}
        self.df = Counter()   # document frequency per term
        self.idf = {}
        self._build()

    def _build(self):
        for path in sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))):
            source = os.path.basename(path)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for ch in _chunk(text):
                toks = Counter(_tokenize(ch))
                if not toks:
                    continue
                self.chunks.append({"source": source, "text": ch, "tokens": toks})
                for term in toks:
                    self.df[term] += 1
        n = max(len(self.chunks), 1)
        self.idf = {t: math.log((n + 1) / (df + 1)) + 1 for t, df in self.df.items()}

    def retrieve(self, query, k=4):
        q = Counter(_tokenize(query))
        if not q:
            return []
        scored = []
        for ch in self.chunks:
            # idf-weighted overlap, length-normalised
            score = sum(min(q[t], ch["tokens"][t]) * self.idf.get(t, 0.0) for t in q)
            if score > 0:
                score /= math.sqrt(sum(ch["tokens"].values()))
                scored.append((score, ch))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ch for _, ch in scored[:k]]


_INDEX = None


def _index():
    global _INDEX
    if _INDEX is None:
        _INDEX = _Index()
    return _INDEX


def retrieve_context(query, k=4, max_chars=3500):
    """Return a formatted context block of the top-k doc chunks, or ''."""
    hits = _index().retrieve(query, k=k)
    if not hits:
        return ""
    out, total = [], 0
    for h in hits:
        block = f"[source: {h['source']}]\n{h['text']}"
        if total + len(block) > max_chars:
            break
        out.append(block)
        total += len(block)
    return "\n\n---\n\n".join(out)
