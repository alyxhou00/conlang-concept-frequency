# 04. Vocabulary

Lexicon version {{version}}.

## How words are made / 造詞方式

1. Every concept (from [Concepticon](https://concepticon.clld.org), plus a few of our own) gets a frequency: how often it is used across English, Spanish, German, Chinese and Japanese.
2. Huffman coding turns frequencies into word lengths: frequent concepts get 1 syllable, rarer ones 2 or 3.
3. Among words of the same length, syllables with fewer letters go to more frequent concepts, and neighbouring syllables share no sound, so frequent words don't sound alike.
4. 10% of the two-syllable words are kept free for words added later (see [00 Introduction](00-introduction.md#versions--版本)).

Some concepts don't get a word of their own:

- **Pronouns**: 33 pronoun concepts (ME, MY, HIS, WE TWO …) use one of the 7 pronouns.
- **Compounds**: concepts made of existing concepts are said with those words, head first: COCONUT TREE → TREE COCONUT ({{w: COCONUT_TREE}}).

## Numbers / 數字

{{stats}}

## The 30 most frequent words / 最常用的 30 個詞

{{top: 30}}

## Full list / 完整詞表

[lexicon/{{version}}.tsv](../lexicon/{{version}}.tsv): every concept with its word, syllables, the spelling with zero consonants (`cvc`) and IPA. `rank` orders the words from most to least frequent. The frequencies themselves are not published (see [ATTRIBUTION.md](../ATTRIBUTION.md)).
