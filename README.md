# conlang-concept-frequency

We want to create a constructed language (conlang) in which the concepts people use most often get the shortest words: we estimate how often each concept is used across many languages and assign word lengths with Huffman coding. Related concepts share words, because the grammar is analytic (derived and new concepts are compounds of existing words).

The language itself (phonology, orthography, grammar, vocabulary, texts) is described in [docs/](docs/README.md).

## Setup

Python 3.13.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

The data repositories are not committed here. Clone them into `data/` at the commits we used:

```bash
git clone https://github.com/concepticon/concepticon-data.git data/concepticon-data
git -C data/concepticon-data checkout a89063d5657022a4ac11c557baef4958809e7c91
git clone https://github.com/concepticon/norare-data.git data/norare-data
git -C data/norare-data checkout 4b8901d6fa3d6cc14afbde6bf2fb061d4a4ab2c4
```

Japanese words come from the Japanese WordNet inside the Open Multilingual Wordnet 1.4 (the same file NLTK downloads):

```bash
curl -L -o data/omw-1.4.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/omw-1.4.zip
```

## Layout

| Folder or file | Contents |
| --- | --- |
| [`pipeline/`](pipeline/README.md) | The scripts that build, release and render the lexicon |
| [`mapping/`](mapping/README.md) | Hand-edited tables: our own concepts, merged pronouns, compounds |
| [`lexicon/`](lexicon/CHANGELOG.md) | Released versions: `<version>.tsv` (concepts and words), `<version>.json` (statistics), `CHANGELOG.md` |
| `texts/` | Concept-tagged texts, e.g. UDHR Article 1 |
| `docs/` | Pages about the language: 00 Introduction … 06 Culture, A Pipeline; generated from `docs/src/` by `docs/build_docs.py` |
| [`checks/`](checks/README.md) | A one-off check of the data sources, not part of the pipeline |
| `tests/` | Tests (`pytest`) |
| `notes/` | The design discussion (Traditional Chinese) |
| `data/` | Downloaded data: Concepticon and NoRaRe clones, OMW zip, and for the coverage check `udhr2/` and `tatoeba/` (not committed) |
| `out/` | Generated tables (not committed, see Licenses) |
| `ATTRIBUTION.md` | Licenses and attribution statements for the data we use |
| `REFERENCES.md` | Literature (參考文獻) |

## Running the pipeline

```bash
.venv/Scripts/python -X utf8 pipeline/build_concept_freq.py
.venv/Scripts/python -X utf8 pipeline/build_lexicon.py
.venv/Scripts/python -X utf8 pipeline/render.py texts/udhr-article-1.txt
```

1. `build_concept_freq.py` estimates how often each concept is used (`out/concept_freq.tsv`).
2. `build_lexicon.py` gives each concept a word, shorter for more frequent ones (`out/lexicon.tsv`, a draft).
3. `render.py` prints a text in our language, with IPA and glosses.

`-X utf8` is only needed on Windows consoles not set to UTF-8.

- Data sources, options and how words are assigned: [pipeline/README.md](pipeline/README.md)
- Publishing a new lexicon version: [docs/A-pipeline.md](docs/A-pipeline.md); current version and history: [lexicon/CHANGELOG.md](lexicon/CHANGELOG.md)
- Texts in `texts/` are written with concept names, so they stay valid when the words change: `PERSON ALL BE_BORN FREE AND EQUAL …` (format: [pipeline/README.md](pipeline/README.md#renderpy-texts))

## Tests and checks

```bash
.venv/Scripts/python -m pytest
.venv/Scripts/python -X utf8 checks/check_sources.py
```

## Licenses

Our data sources have different licenses, and NoRaRe is **non-commercial only** (CC BY-NC 4.0). See [ATTRIBUTION.md](ATTRIBUTION.md) before redistributing any derived frequency tables; for that reason `out/` is not committed. No license has been chosen yet for this repository's own code.

## Notes
The plan and our discussion with AI are in [人造語言：跨語言概念頻率與編碼.md](notes/人造語言：跨語言概念頻率與編碼.md).