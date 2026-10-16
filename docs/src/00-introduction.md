# 00. Introduction

- Name / 名稱: not decided yet
- Language code / 語言代碼: not decided yet
- Type / 類型: constructed language, analytic (isolating) / 人造語言，分析語（孤立語）

## Goals / 目標

1. **Frequent concepts get short words.** How often each concept is used is estimated across five languages (English, Spanish, German, Chinese, Japanese) and turned into word lengths with Huffman coding.
2. **Derived concepts share a root.** Related concepts should sound related, like Arabic *k-t-b* in *kataba* "write" and *kitāb* "book". Not built yet.
3. **Sentences as short as possible.** No grammatical category has to be marked; particles are used only when needed.

## Design principles / 設計原則

- Concepts, not words, are the unit: the concept list is [Concepticon](https://concepticon.clld.org) (4,099 concepts) plus a few of our own.
- Every concept's word is built from CVC syllables (see [01 Phonology](01-phonology.md)).
- Frequent words should not sound alike: neighbouring syllables in the code share no sound.
- Compound concepts are said with existing words (COCONUT TREE → TREE COCONUT) instead of getting their own word.

## Versions / 版本

Semantic versioning:

- **0.x (beta)**: words may still change between versions.
- **1.0.0**: the word list is frozen. From then on, existing words never change.
- **1.x**: only adds new words. New words go into free code space, so the prefix property holds and no old word moves. 10% of the two-syllable space is kept free for them.
- **2.0.0**: only if an existing word ever has to change.

A removed word's slot is never reused.

Before 1.0.0: root families, a check of common texts for missing concepts, the number system, and the remaining grammar (tense, relative clauses, comparison).

## Status / 狀態

- Phonology, orthography and core grammar: decided.
- Vocabulary: generated for 4,108 concepts.
- Root families (goal 2), numbers, tense details, name: not decided.
