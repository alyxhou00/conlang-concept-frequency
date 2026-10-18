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

The first writes `out/concept_freq_by_lang.tsv` and `out/concept_freq.tsv`; the second writes `out/lexicon.tsv`; the third prints the text in our language, with IPA and glosses. `-X utf8` is needed on Windows consoles that are not set to UTF-8.

`mapping/compounds.tsv` is generated once and then edited by hand. To regenerate it from scratch (this overwrites hand edits):

```bash
.venv/Scripts/python -X utf8 pipeline/find_compounds.py
```

### Releasing a version

The current lexicon is version **0.1.0** (beta). Versions follow semantic versioning: 0.x betas may still change words; from 1.0.0 on, existing words never change and 1.x only adds words, into the 10% of two-syllable code space that `build_lexicon.py` keeps free (`--reserve-2syl`, default 0.10).

```bash
.venv/Scripts/python -X utf8 pipeline/release.py 0.2.0 --note "what changed"
.venv/Scripts/python -X utf8 docs/build_docs.py
```

`release.py` writes `lexicon/<version>.tsv` (rank, concept, kind, word, syllables, `cvc`, IPA; no frequencies) and `lexicon/<version>.json`, and adds a `lexicon/CHANGELOG.md` entry. An existing version is never overwritten. `build_docs.py` then fills the pages in `docs/` from the latest version; edit their templates in `docs/src/`. A test fails if `docs/` is out of date.

### Writing texts

A text in `texts/` names concepts, not words, so it stays valid when the lexicon changes. One sentence per line; lines starting with `# ` are comments. A token is a concept gloss with `_` for spaces (`BE_BORN`, `SPIRIT_(ATTITUDE)`), or `#` + a concept ID (`#1209`). Punctuation `. , ? ! ; :` is kept. Word order follows the grammar in the discussion doc (SVO; modifiers, particles and postpositions after their word):

```
PERSON ALL BE_BORN FREE AND EQUAL DIGNITY AND RIGHT_(ENTITLEMENT) IN .
```

### Where the frequencies come from

The lexicon covers all 4,099 active Concepticon concept sets plus our 9 concepts in `mapping/extra_concepts.tsv`. Retired Concepticon concepts (66 sets that have a `REPLACEMENT_ID`) count for their replacement. For each concept and language (en, es, de, zh, ja), in order of preference:

1. **A frequency list**: NoRaRe subtitle frequencies for en, es, de, zh; for ja, the Japanese WordNet word (via Bond-2013-OMW) looked up in wordfreq.
2. **Otherwise wordfreq**: candidate words for the concept come from the word columns of all Concepticon concept lists and NoRaRe datasets (522 lists have English, about 50 each Spanish and Chinese, 36 German, 8 Japanese), plus the Concepticon name itself for English, and `mapping/extra_concepts.tsv` for our own concepts. Notes in brackets are removed and alternatives are split (`ronsoco, carpincho`, `arm or hand`). The chosen candidate is a single word if possible, then the one most lists agree on, then the most frequent. Phrases with spaces are not used, because wordfreq rates a phrase almost as frequent as its rarest word.
3. **No data at all** (124 concepts, mostly compounds such as COCONUT TREE): the concept gets the lowest frequency in the table. Many of these are said with existing words anyway (see compounds below).

The `source` column of `out/concept_freq_by_lang.tsv` shows which case applies.

### `pipeline/build_concept_freq.py` options

**`--min-langs N`** (default 0): keep only concepts that have frequency data in at least N of the 5 languages. With 0, every concept is kept, including those with no data (case 3 above). Concepts below N are left out of the lexicon entirely.

- Higher N means each kept concept's frequency rests on more languages, so it is less biased by one language and less affected by one bad word mapping. But fewer concepts are kept.
- Lower N keeps more concepts. But some get their frequency from one or two languages only, often English, which has the most word lists.
- Results with the default sound inventory:

| `--min-langs` | Concepts | With their own word | Average word length |
| --- | --- | --- | --- |
| 0 (default) | 4,108 | 3,752 | 1.159 syllables, 2.32 letters |
| 1 | 3,984 | 3,681 | 1.159 syllables, 2.32 letters |
| 2 | 3,393 | 3,206 | 1.157 syllables, 2.31 letters |
| 3 | 2,521 | 2,468 | 1.134 syllables, 2.21 letters |
| 4 | 1,819 | 1,795 | 1.110 syllables, 2.16 letters |
| 5 | 948 | 946 | 1.053 syllables, 1.88 letters |

The average is per word, weighted by how often each word is used.

0 and 1 give the same average, because the concepts without data are so rare that they barely affect it.

**`--outlier-factor F`** (default 10): when averaging a concept over its languages, ignore a language whose value is more than F times above or below the median of that concept's languages (compared on a log scale). This catches bad word mappings, such as Japanese 水 for WATER BUFFALO or German *Oheim* for UNCLE. If every language of a concept would be dropped, all are kept. `0` turns this off. Dropped languages are listed in the `outliers` column of `out/concept_freq.tsv`.

### `pipeline/build_lexicon.py` options

**`--onsets`** (default `Ømnptkshvrl`), **`--vowels`** (default `iöeuëoa`), **`--codas`** (default `nthlØ`): the sound inventory, one letter per sound. `Ø` is the zero consonant: it counts as a consonant slot but is not written in the word.

| Slot | IPA | Letters |
| --- | --- | --- |
| Onset (syllable start) | ∅ m n p t k s x ʋ ʁ l | Ø m n p t k s h v r l |
| Vowel | i ø ɛ u ɤ ɔ ɑ | i ö e u ë o a |
| Coda (syllable end) | n t x l ∅ | n t h l Ø |

Within each node of the code tree, the most frequent concepts get syllables in this order:

1. Fewer letters first, so frequent words are shorter on paper.
2. Within the same number of letters, each slot cycles: the next syllable takes the onset, vowel and coda used least recently. Neighbouring syllables then share no written letter, so the most frequent words don't sound alike (*in mö nu ëh po al ti …* rather than *in it il ön öt …*). When the onset, vowel and coda counts share no common factor, this is the simple cycle "syllable k = onset k, vowel k, coda k". When they do (10 onsets and 5 codas share 5), the simple cycle would repeat, but this rule still uses every syllable once.

A zero onset is allowed only in a word's first syllable, so every written word splits into syllables in exactly one way. At the start of a word it is pronounced as a glottal stop [ʔ] but not written. Without that, continuous speech would be ambiguous across words: "et e" would sound like "e te". With it they are [ʔɛt ʔɛ] and [ʔɛ tɛ]. The first syllable of a word has 11 × 7 × 5 = 385 options; later syllables have 10 × 7 × 5 = 350.

### Which concepts get their own word

- **Merged** (`mapping/merges.tsv`): the 33 Concepticon pronoun concepts become 7 pronouns: I, THOU (you, singular), YOU (you, plural), WE (EXCLUSIVE), WE (INCLUSIVE), HE OR SHE OR IT, THEY. Case and possessive forms (ME, MY, HIS …), duals (WE TWO …) and honorifics merge into these. Their frequency is added to the target; WE, US, OUR and WE TWO, which don't say whether the listener is included, are split half and half.
- **Compounds** (`mapping/compounds.tsv`, 331 used): a concept whose name consists of existing concepts is said with those words in our word order, e.g. COCONUT TREE → TREE COCONUT, NOT HAVE → HAVE NOT, PUT IN ORDER → PUT ORDER IN. Each part gets the compound's frequency on top of its own.
- Everything else (3,752 concepts) gets its own word.

`out/lexicon.tsv` has one row per concept: `kind` (word, merged, compound), `p` (the concept's frequency), `p_word` (the frequency of the word itself, including what merged and compound concepts add), and the word as written (`word`), with syllable breaks (`word_hyphenated`), with the zero consonants (`cvc`, e.g. `ØöØ.hiØ`), and in IPA (`ipa`).

## Tests and checks

```bash
.venv/Scripts/python -m pytest
.venv/Scripts/python -X utf8 checks/check_sources.py
```

## Licenses

Our data sources have different licenses, and NoRaRe is **non-commercial only** (CC BY-NC 4.0). See [ATTRIBUTION.md](ATTRIBUTION.md) before redistributing any derived frequency tables; for that reason `out/` is not committed. No license has been chosen yet for this repository's own code.

## Notes
The plan and our discussion with AI are in [人造語言：跨語言概念頻率與編碼.md](notes/人造語言：跨語言概念頻率與編碼.md).