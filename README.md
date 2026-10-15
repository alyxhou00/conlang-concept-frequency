# conlang-concept-frequency

We want to create a constructed language (conlang) in which the concepts people use most often get the shortest words and related concepts share a root (like Arabic k-t-b in *kataba* "write" and *kitāb* "book"), so we estimate how often each concept is used across many languages, group related concepts into root families, and assign word lengths with Huffman coding.

The plan and our discussion are in [人造語言：跨語言概念頻率與編碼.md](人造語言：跨語言概念頻率與編碼.md).

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

| Path | Contents |
| --- | --- |
| `data/` | Concepticon and NoRaRe clones, OMW zip (not committed) |
| `freq/build_concept_freq.py` | Step 1–3: concept frequencies per language (en, es, de, zh, ja) and combined |
| `encode/huffman.py` | n-ary Huffman coding |
| `encode/build_lexicon.py` | Step 4: give every concept a word made of CVC syllables |
| `tests/` | Tests for the encoder (`pytest`) |
| `out/` | Generated tables (not committed, see Licenses) |
| `checks/check_sources.py` | Sanity checks on Calude-2011-200, NoRaRe and wordfreq |
| `checks/check_sources_output.txt` | Output of the last run |
| `ATTRIBUTION.md` | Licenses and attribution statements for the data we use |
| `REFERENCES.md` | Literature (參考文獻) |

Planned (from the discussion doc): `mapping/`, `notebooks/`.

## Running the pipeline

```bash
.venv/Scripts/python -X utf8 freq/build_concept_freq.py
.venv/Scripts/python -X utf8 encode/build_lexicon.py
```

The first writes `out/concept_freq_by_lang.tsv` and `out/concept_freq.tsv`; the second writes `out/lexicon.tsv`. Options:

- `build_concept_freq.py --min-langs 3`: keep concepts with data in at least this many of the 5 languages.
- `build_lexicon.py --consonants ptkbdgmnslfh --vowels aeiou`: the sound inventory, one letter each. The defaults give 12 × 5 × 12 = 720 CVC syllables.

`-X utf8` is needed on Windows consoles that are not set to UTF-8.

## Tests and checks

```bash
.venv/Scripts/python -m pytest
.venv/Scripts/python -X utf8 checks/check_sources.py
```

## Licenses

Our data sources have different licenses, and NoRaRe is **non-commercial only** (CC BY-NC 4.0). See [ATTRIBUTION.md](ATTRIBUTION.md) before redistributing any derived frequency tables; for that reason `out/` is not committed. No license has been chosen yet for this repository's own code.
