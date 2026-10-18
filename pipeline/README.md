# pipeline/

The scripts that turn concepts into words. Run them from the project folder; the order and how to publish a version are in [docs/A-pipeline.md](../docs/A-pipeline.md).

| Script | Does | Writes |
| --- | --- | --- |
| `build_concept_freq.py` | estimates how often each concept is used | `out/concept_freq.tsv`, `out/concept_freq_by_lang.tsv` |
| `build_lexicon.py` | gives each concept a word, shorter for more frequent ones | `out/lexicon.tsv` (a draft) |
| `release.py` | freezes the draft as a version | `lexicon/<version>.tsv`, `.json`, a `CHANGELOG.md` entry |
| `render.py` | prints a text in our language, with IPA and glosses | |
| `find_compounds.py` | drafts `mapping/compounds.tsv` | `mapping/compounds.tsv` |

`huffman.py`, `units.py` and `phonetics.py` are helpers.

## build_concept_freq.py: how often each concept is used

The concepts are all 4,099 active Concepticon concept sets plus our 9 in `mapping/extra_concepts.tsv`. A retired Concepticon concept (66 sets with a `REPLACEMENT_ID`) counts for its replacement.

For each concept and each language (en, es, de, zh, ja), the frequency comes from the first of these that has data. The `source` column of `out/concept_freq_by_lang.tsv` says which.

1. **A frequency list**: NoRaRe subtitle frequencies for en, es, de, zh; for ja, the Japanese WordNet word (via Bond-2013-OMW) looked up in wordfreq.
2. **wordfreq**, on a word chosen from the word columns of all Concepticon concept lists and NoRaRe datasets (522 lists have English, about 50 each Spanish and Chinese, 36 German, 8 Japanese), plus the Concepticon name for English and `mapping/extra_concepts.tsv` for our own concepts. Notes in brackets are removed and alternatives split (`ronsoco, carpincho`, `arm or hand`). We prefer a single word, then the one most lists agree on, then the most frequent. Phrases are never used, because wordfreq rates a phrase almost as frequent as its rarest word.
3. **No data** (124 concepts, mostly compounds such as COCONUT TREE): the lowest frequency in the table. Many of these are compounds anyway (see below).

The languages are then averaged into `out/concept_freq.tsv`.

**`--outlier-factor F`** (default 10): in that average, ignore a language more than F times above or below the concept's median (on a log scale). This catches bad word mappings, such as Japanese 水 for WATER BUFFALO or German *Oheim* for UNCLE. If this would drop every language, all are kept. `0` turns it off. Dropped languages are listed in the `outliers` column.

**`--min-langs N`** (default 0): leave out of the lexicon every concept with data in fewer than N of the 5 languages. A higher N makes each frequency rest on more languages (less English bias, less harm from one bad mapping) but keeps fewer concepts:

| `--min-langs` | Concepts | With their own word | Average word length |
| --- | --- | --- | --- |
| 0 (default) | 4,108 | 3,752 | 1.159 syllables, 2.32 letters |
| 1 | 3,984 | 3,681 | 1.159 syllables, 2.32 letters |
| 2 | 3,393 | 3,206 | 1.157 syllables, 2.31 letters |
| 3 | 2,521 | 2,468 | 1.134 syllables, 2.21 letters |
| 4 | 1,819 | 1,795 | 1.110 syllables, 2.16 letters |
| 5 | 948 | 946 | 1.053 syllables, 1.88 letters |

With the default sound inventory; the average is weighted by how often each word is used, so the rare no-data concepts (0 vs 1) barely change it.

## build_lexicon.py: the words

**Which concepts get a word.** Two tables in [`mapping/`](../mapping/README.md) say which concepts reuse other words; each passes its frequency on to the words it uses.

- **Merged** (`merges.tsv`): the 33 Concepticon pronoun concepts become 7 pronouns: I, THOU (you, singular), YOU (you, plural), WE (EXCLUSIVE), WE (INCLUSIVE), HE OR SHE OR IT, THEY. Case and possessive forms (ME, MY, HIS …), duals (WE TWO …) and honorifics merge into these. WE, US, OUR and WE TWO, which don't say whether the listener is included, are split half and half.
- **Compounds** (`compounds.tsv`, 331 used): a concept whose name is made of existing concepts is said with those words, in our word order: COCONUT TREE → TREE COCONUT, NOT HAVE → HAVE NOT, PUT IN ORDER → PUT ORDER IN.
- Everything else (3,752 concepts) gets its own word.

**Sounds.** `--onsets` (default `Ømnptkshvrl`), `--vowels` (default `iöeuëoa`) and `--codas` (default `nthlØ`) set the inventory, one letter per sound. `Ø` is the zero consonant: it fills a consonant slot but is not written.

| Slot | IPA | Letters |
| --- | --- | --- |
| Onset (syllable start) | ∅ m n p t k s x ʋ ʁ l | Ø m n p t k s h v r l |
| Vowel | i ø ɛ u ɤ ɔ ɑ | i ö e u ë o a |
| Coda (syllable end) | n t x l ∅ | n t h l Ø |

A zero onset is allowed only in a word's first syllable, where it is said as a glottal stop [ʔ]. So every word splits into syllables in one way only, and speech is unambiguous across words: "et e" is [ʔɛt ʔɛ], "e te" is [ʔɛ tɛ]. A first syllable has 11 × 7 × 5 = 385 options, a later one 10 × 7 × 5 = 350.

**Which syllable goes to which concept.** Word lengths come from Huffman coding over these syllables. Within each node of the code tree, the most frequent concepts get:

1. syllables with fewer letters first, so frequent words are also short on paper;
2. among equally long syllables, the onset, vowel and coda used least recently. Neighbouring syllables then share no letter, so the most frequent words don't sound alike (*in mö nu ëh po al ti …*, not *in it il ön öt …*). This still uses every syllable once when the slot counts share a factor (10 onsets and 5 codas), where a plain "onset k, vowel k, coda k" cycle would repeat.

**`--reserve-2syl`** (default 0.10): the share of two-syllable words kept free, so that versions after 1.0.0 can add words without changing old ones.

**Output.** `out/lexicon.tsv` has one row per concept: `kind` (word, merged, compound), `p` (the concept's frequency), `p_word` (the word's frequency, including what merged and compound concepts add), and the word as written (`word`), with syllable breaks (`word_hyphenated`), with zero consonants (`cvc`, e.g. `ØöØ.hiØ`) and in IPA (`ipa`).

## release.py: versions

```bash
.venv/Scripts/python -X utf8 pipeline/release.py 0.2.0 --note "what changed"
```

Writes `lexicon/<version>.tsv` (rank, concept, kind, word, syllables, `cvc`, IPA; no frequencies, see [ATTRIBUTION.md](../ATTRIBUTION.md)) and `lexicon/<version>.json` (statistics), and adds an entry to `lexicon/CHANGELOG.md`. It never overwrites an existing version. Then run `docs/build_docs.py`; a test fails if `docs/` is out of date. Which number to pick: [docs/A-pipeline.md](../docs/A-pipeline.md).

## render.py: texts

A text in `texts/` names concepts, not words, so it stays valid when the words change. One sentence per line; lines starting with `# ` are comments. A token is a concept gloss with `_` for spaces (`BE_BORN`, `SPIRIT_(ATTITUDE)`) or `#` + a concept ID (`#1209`); the punctuation `. , ? ! ; :` is kept. Word order follows the [grammar](../docs/03-grammar.md): SVO, with modifiers, particles and postpositions after their word.

```
PERSON ALL BE_BORN FREE AND EQUAL DIGNITY AND RIGHT_(ENTITLEMENT) IN .
```

## find_compounds.py

`mapping/compounds.tsv` was drafted by this script and then edited by hand. Running it again starts over and **overwrites the hand edits**.
