# 04. Vocabulary

## How words are made / 造詞方式

1. Every concept (from [Concepticon](https://concepticon.clld.org), plus a few of our own) gets a frequency: how often it is used across English, Spanish, German, Chinese and Japanese.
2. Huffman coding turns frequencies into word lengths: frequent concepts get 1 syllable, rarer ones 2 or 3.
3. Among words of the same length, syllables with fewer letters go to more frequent concepts, and neighbouring syllables share no sound, so frequent words don't sound alike.

Some concepts don't get a word of their own:

- **Pronouns**: 33 pronoun concepts (ME, MY, HIS, WE TWO …) use one of the 7 pronouns.
- **Compounds**: 331 concepts are said with existing words, head first: COCONUT TREE → TREE COCONUT (*isu öhkoh*).

**The words change** whenever the concept list or the frequencies change. Texts are therefore written with concept names and turned into words by a script (see [A Pipeline](A-pipeline.md)).

## Numbers / 數字

| | |
| --- | --- |
| Concepts | 4,108 |
| With their own word | 3,752 |
| 1 / 2 / 3 syllables | 376 / 3,149 / 227 |
| Average word, weighted by use | 1.16 syllables, 2.32 letters |

## The 30 most frequent words / 最常用的 30 個詞

Snapshot of commit `dc2a569`.

| Concept | Word | IPA |
| --- | --- | --- |
| I | ö | [ʔø] |
| HE OR SHE OR IT | e | [ʔɛ] |
| NOT | ë | [ʔɤ] |
| WHAT | o | [ʔɔ] |
| THOU | a | [ʔɑ] |
| AND | in | [ʔin] |
| PAST (PARTICLE) | mö | [mø] |
| THAT | nu | [nu] |
| AT | ëh | [ʔɤx] |
| IN | po | [pɔ] |
| FOR | al | [ʔɑl] |
| WITH | ti | [ti] |
| ATOP OR UP | ön | [ʔøn] |
| NO | ut | [ʔut] |
| YOU | së | [ɕɤ] |
| THIS | oh | [ʔɔx] |
| YES | ha | [xɑ] |
| HOW | il | [ʔil] |
| HAVE | vö | [ʋø] |
| GOOD | en | [ʔɛn] |
| BE | ru | [ʁu] |
| BUT | ët | [ʔɤt] |
| THEY | lo | [lɔ] |
| IF | ah | [ʔɑx] |
| LONG AGO | öl | [ʔøl] |
| WE (EXCLUSIVE) | ne | [nɛ] |
| HERE | un | [ʔun] |
| WE (INCLUSIVE) | pë | [pɤ] |
| ONE | ot | [ʔɔt] |
| OF THIS KIND (SUCH) | ta | [tɑ] |

## Full list / 完整詞表

`out/lexicon.tsv`, made by the pipeline. It is not committed, because it is derived from frequency data whose licenses don't allow redistributing it as it is (see [ATTRIBUTION.md](../ATTRIBUTION.md)).
