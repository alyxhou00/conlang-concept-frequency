# A. Pipeline

How the vocabulary is generated. Setup and all options are in the [main README](../README.md).

```bash
.venv/Scripts/python -X utf8 freq/build_concept_freq.py      # concept frequencies
.venv/Scripts/python -X utf8 encode/build_lexicon.py         # words
.venv/Scripts/python -X utf8 encode/render.py texts/udhr-article-1.txt   # a text in our language
```

| Step | File | Output |
| --- | --- | --- |
| Frequencies | `freq/build_concept_freq.py` | `out/concept_freq.tsv` |
| Our own concepts | `mapping/extra_concepts.tsv` | (input) |
| Pronouns → 7 | `mapping/merges.tsv` | (input) |
| Compounds | `mapping/compounds.tsv` (edit by hand) | (input) |
| Words | `encode/build_lexicon.py` | `out/lexicon.tsv` |
| Texts | `encode/render.py` + `texts/*.txt` | printed text, IPA, glosses |

## Writing a text / 寫文章

Write concept names in our word order, one sentence per line, with `_` for spaces:

```
PERSON ALL BE_BORN FREE AND EQUAL DIGNITY AND RIGHT_(ENTITLEMENT) IN .
```

Then render it. Because the text names concepts, it stays valid when the words change.
