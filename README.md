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

The first writes `out/concept_freq_by_lang.tsv` and `out/concept_freq.tsv`; the second writes `out/lexicon.tsv`. `-X utf8` is needed on Windows consoles that are not set to UTF-8.

### `freq/build_concept_freq.py` options

**`--min-langs N`** (default 3): keep only concepts that have frequency data in at least N of the 5 languages (en, es, de, zh, ja). Concepts with data in fewer languages are left out of the lexicon entirely.

- Higher N means the frequency of each kept concept rests on more languages, so it is less biased by one language and less affected by one bad word mapping. But fewer concepts are kept.
- Lower N keeps more concepts. But some of them get their frequency from one or two languages only, often English, which has the largest list.
- Results with the default sound inventory:

| `--min-langs` | Concepts | Average word length |
| --- | --- | --- |
| 1 | 3,165 | 1.136 syllables, 2.27 letters |
| 2 | 2,505 | 1.119 syllables, 2.20 letters |
| 3 (default) | 1,875 | 1.095 syllables, 2.09 letters |
| 4 | 1,258 | 1.067 syllables, 1.94 letters |
| 5 | 569 | 1.031 syllables, 2.11 letters |

**`--outlier-factor F`** (default 10): when averaging a concept over its languages, ignore a language whose value is more than F times above or below the median of that concept's languages (compared on a log scale). This catches bad word mappings, such as Japanese 水 for WATER BUFFALO or German *Oheim* for UNCLE. If every language of a concept would be dropped, all are kept. `0` turns this off. Dropped languages are listed in the `outliers` column of `out/concept_freq.tsv`.

### `encode/build_lexicon.py` options

**`--onsets`** (default `Ømnptkshvrl`), **`--vowels`** (default `iöeuëoa`), **`--codas`** (default `nthlØ`): the sound inventory, one letter per sound. `Ø` is the zero consonant: it counts as a consonant slot but is not written in the word.

| Slot | IPA | Letters |
| --- | --- | --- |
| Onset (syllable start) | ∅ m n p t k ɕ x ʋ ʀ l | Ø m n p t k s h v r l |
| Vowel | i ø ɛ u ɤ ɔ ɑ | i ö e u ë o a |
| Coda (syllable end) | n t x l ∅ | n t h l Ø |

A zero onset is allowed only in a word's first syllable, so every written word splits into syllables in exactly one way. The first syllable of a word has 11 × 7 × 5 = 385 options; later syllables have 10 × 7 × 5 = 350. `out/lexicon.tsv` shows each word as written (`word`), with syllable breaks (`word_hyphenated`), and with the zero consonants (`cvc`, e.g. `ØöØ.hiØ` for *öhi*).

## Tests and checks

```bash
.venv/Scripts/python -m pytest
.venv/Scripts/python -X utf8 checks/check_sources.py
```

## Licenses

Our data sources have different licenses, and NoRaRe is **non-commercial only** (CC BY-NC 4.0). See [ATTRIBUTION.md](ATTRIBUTION.md) before redistributing any derived frequency tables; for that reason `out/` is not committed. No license has been chosen yet for this repository's own code.
