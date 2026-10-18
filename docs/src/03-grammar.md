# 03. Grammar

Principle: **sentences as short as possible.** Nothing has to be marked; particles are added only when needed. The language is analytic (isolating): words never change form.

Examples show concept names (GLOSSES) and the words in lexicon version {{version}}.

## Overview / 總覽

| Topic | Decision | Example |
| --- | --- | --- |
| Word order | SVO | I SEE DOG — {{w: I SEE DOG}} |
| Modifiers | After the noun (adjectives, possessors, relative clauses, numerals) | DOG BIG — {{w: DOG BIG}} |
| Particles | After the word they modify | GO NOT — {{w: GO NOT}} |
| Adpositions | Postpositions | DIGNITY IN — {{w: DIGNITY IN}} |
| Obligatory marking | None (number, tense, voice, case all optional) | PERSON = one person or many |
| Yes/no questions | Question particle at the start | Q THOU GO — {{w: QUESTION_(PARTICLE) THOU GO}} |
| Question words | Stay in place | THOU SEE WHO — {{w: THOU SEE WHO}} |
| Copula | Adjectives are predicates directly; BE only before a noun | PERSON FREE — {{w: PERSON FREE}}; HE BE TEACHER — {{w: HE BE TEACHER}} |
| Possession | Juxtaposed, possessor after | DOG I — {{w: DOG I}} "my dog" |
| Numerals | After the noun, no classifiers | PERSON THREE — {{w: PERSON THREE}} |
| Compounds | Existing words, head first | TREE COCONUT — {{w: COCONUT_TREE}} |
| Adverbs | At the end of the clause | HE BLOW HARD — {{w: HE BLOW_(OF_WIND) HARD}} |
| Comparison | A ADJ MORE B ABOVE; B can be left out | SUN STRONG MORE HE ABOVE — {{w: SUN STRONG MORE HE ABOVE}} "the sun is stronger than he" |
| Clauses | Joined with commas, no conjunction needed | see [Clauses](#clauses--子句) |

## Particles / 小詞

| Particle | Word | Use |
| --- | --- | --- |
| NOT | {{w: NOT}} | after the verb: GO NOT |
| PAST | {{w: PAST_(PARTICLE)}} | after the verb, only when needed: GO PAST |
| PLURAL | {{w: PLURAL_(PARTICLE)}} | after the noun, only when needed: PERSON PL |
| QUESTION | {{w: QUESTION_(PARTICLE)}} | at the start of a yes/no question |
| SHOULD | {{w: SHOULD}} | after the verb: DO SHOULD |

## Clauses / 子句

Clauses are joined with a comma (a pause in speech). There is no word for "that" or "who"; the comma does the work, and the order of the parts says how they relate.

| Kind | Rule | Example |
| --- | --- | --- |
| "that"-clause | After the verb, set off by a comma | THEY AGREE , SUN STRONG MORE — {{w: THEY AGREE , SUN STRONG MORE}} "they agree that the sun is stronger" |
| Question as object | The question word stays in place, after a comma | DISPUTE , WHICH STRONG MORE — {{w: DISPUTE , WHICH STRONG MORE}} "argue about which is stronger" |
| Relative clause | After the noun, between commas | PERSON TRAVEL , WRAP CLOAK WARM , COME — {{w: PERSON TRAVEL , WRAP CLOAK WARM , COME}} "a traveller, wrapped in a warm cloak, came" |
| "when"-clause | WHEN at the end of the clause, like a postposition | HE BLOW MORE WHEN , … — {{w: HE BLOW_(OF_WIND) MORE WHEN ,}} "when he blew harder, …" |
| "the more …, the more …" | MORE in both clauses, the first one ending in WHEN | HE BLOW MORE WHEN , PERSON TRAVEL WRAP CLOAK TIGHT MORE — {{w: HE BLOW_(OF_WIND) MORE WHEN , PERSON TRAVEL WRAP CLOAK TIGHT MORE}} |
| "so", "therefore" | RESULT IN at the start, "in the result", like LAST IN "in the end" | RESULT IN , … — {{w: RESULT IN ,}} |
| "but", "and" | BUT at the start of the second clause; AND can be left out | …, BUT HE BLOW MORE WHEN , … |

A passive is not needed: "wrapped in a cloak" is WRAP CLOAK, and "should be considered stronger" is just STRONG MORE.

Modals (SHOULD, MUST, CAN) go after the verb, like the particles: ADMIT MUST — {{w: ADMIT MUST}} "must admit".

Decided while translating *The North Wind and the Sun* ([texts/north-wind-and-sun.txt](../texts/north-wind-and-sun.txt)). Open point: in writing the commas are clear, but in speech one pause marks every kind of clause boundary. Check this on longer texts before 1.0.0.

## Pronouns / 代名詞

Singular vs. plural, and inclusive vs. exclusive "we". No gender, no politeness levels, no case: the same word is subject, object and possessor.

| | Singular | Plural |
| --- | --- | --- |
| 1st | I — {{w: I}} | WE (EXCLUSIVE) — {{w: WE_(EXCLUSIVE)}}; WE (INCLUSIVE) — {{w: WE_(INCLUSIVE)}} |
| 2nd | THOU — {{w: THOU}} | YOU — {{w: YOU}} |
| 3rd | HE OR SHE OR IT — {{w: HE_OR_SHE_OR_IT}} | THEY — {{w: THEY}} |

## Proper names and loanwords / 專有名詞與外來詞

| Kind | Rule | Example |
| --- | --- | --- |
| New concepts, including international ones (computer, internet) | Said with existing words, like Chinese 電話 "electric speech"; once common, a word of their own from the free slots. No borrowing by sound. | INTERNET → NET COMPUTER, "net of computers" |
| Names made of our own words | **Modifier first**, the reverse of the normal order: the order itself marks a fixed name. Capitalized. | SHORT LANGUAGE — {{name: SHORT LANGUAGE}}, the name of this language; compare LANGUAGE SHORT — {{w: LANGUAGE SHORT}} "a language that is short" |
| Names from other languages (Maria, Paris) | Adapted to our sounds and placed between two NAME particles, so the listener hears where the name starts and ends. Capitalized. A category word (PERSON, CITY, RIVER …) may follow. | NAME *Nuyok* NAME CITY "New York City" |

Why names need the NAME particles: almost every syllable sequence is already a sequence of our words, so a name like *ma-ri-a* would otherwise be heard as three ordinary words.

Not decided yet: the NAME particle itself (it will be added in the next lexicon version), the rules for adapting foreign sounds, and how foreign names are spelled beyond the capital letter.

## Not decided yet / 尚未決定

- Tense and aspect beyond PAST (future, perfective …).
- Where BY (PASSIVE MARKER) goes, and whether a passive is needed at all.
- Whether commas alone are clear enough in speech (see [Clauses](#clauses--子句)).
- Numbers above ten.
