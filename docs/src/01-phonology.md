# 01. Phonology

## Consonants / 子音

| | Labial | Alveolar | Velar | Uvular | Glottal |
| --- | --- | --- | --- | --- | --- |
| Nasal | m | n | | | |
| Plosive | p | t | k | | (ʔ) |
| Fricative | | s | x | ʁ | |
| Approximant | ʋ | l | | | |

- 10 consonants: /m n p t k s x ʋ ʁ l/.
- /s/ stays [s] before every vowel, also before i: *si* is {{say: si = si}}, not [ɕi], so it stays apart from *hi* {{say: hi = çi}}.
- [ʔ], [ç], [ŋ] are not phonemes; they come from the sound rules below.

## Vowels / 母音

| | Front unrounded | Front rounded | Back unrounded | Back rounded |
| --- | ----------- | ------------- | -------------- | ------------ |
| Close | i         |               |                | u |
| Close-mid |       | ø             | ɤ              |   |
| Open-mid | ɛ      |               |                | ɔ |
| Open |   |        |               | ɑ              |   |

- 7 vowels: /i ø ɛ u ɤ ɔ ɑ/. No length contrast, no diphthongs.

## Syllables / 音節

Every syllable is **C V C**, where either consonant may be empty (written Ø in technical notes):

| Slot | Possible sounds | Count |
| --- | --- | --- |
| Onset (start) | ∅ m n p t k s x ʋ ʁ l | 11 |
| Vowel | i ø ɛ u ɤ ɔ ɑ | 7 |
| Coda (end) | n t x l ∅ | 5 |

- An **empty onset is only allowed in the first syllable of a word**. Inside a word every syllable starts with a consonant, so a word splits into syllables in only one way.
- A word's first syllable has 11 × 7 × 5 = 385 options; later syllables have 10 × 7 × 5 = 350.

## Glottal stop rule / 喉塞音規則

An empty onset at the start of a word is pronounced as a glottal stop [ʔ]:

- *ö* "{{en: ö}}" = {{say: ö = ʔø}}, *in* "{{en: in}}" = {{say: in = ʔin}}.
- This keeps words apart in connected speech: *et e* = {{say: et e = ʔɛt ʔɛ}} vs. *e te* = {{say: e te = ʔɛ tɛ}}.

## h next to a front vowel / h 的顎化

> {h}如前後方是前元音(i, e, ö)則發音變為/ç/

h is [ç] when the vowel right before or right after it in the same word is front (i, e, ö); otherwise it is [x]:

| Word | Sounds | Why |
| --- | --- | --- |
| *hitet* "{{en: hitet}}" | {{say: hitet = çi.tɛt}} | before i |
| *ihu* "{{en: ihu}}" | {{say: ihu = ʔi.çu}} | after i, in the syllable before |
| *utöh* "{{en: utöh}}" | {{say: utöh = ʔu.tøç}} | after ö |
| *hon* "{{en: hon}}" | {{say: hon = xɔn}} | next to o |
| *etpëh* "{{en: etpëh}}" | {{say: etpëh = ʔɛp.pɤx}} | next to ë, a back vowel |

## Coda assimilation / 音節尾同化

> coda {t, n}會受到後方輔音同化成同部位

A coda t or n takes the place of the next consonant when that is a labial (m p) or a velar (k, or h said [x]): t becomes [p] or [k], n becomes [m] or [ŋ]. Only t and n change.

| Next consonant | Coda t | Coda n |
| --- | --- | --- |
| m | *etme* "{{en: etme}}" {{say: etme = ʔɛp.mɛ}} | *önmi* "{{en: önmi}}" {{say: önmi = ʔøm.mi}} |
| p | *etpëh* "{{en: etpëh}}" {{say: etpëh = ʔɛp.pɤx}} | *önkën po* "{{en: önkën po}}" {{say: önkën po = ʔøŋ.kɤm pɔ}} |
| k | *etkal* "{{en: etkal}}" {{say: etkal = ʔɛk.kɑl}} | *önkën* "{{en: önkën}}" {{say: önkën = ʔøŋ.kɤn}} |
| h said [x] | *etha* "{{en: etha}}" {{say: etha = ʔɛk.xɑ}} | *etsuhsen hënöl* "{{en: etsuhsen hënöl}}" {{say: etsuhsen hënöl = ʔɛt.sux.sɛŋ xɤ.nøl}} |
| anything else | *etli* "{{en: etli}}" {{say: etli = ʔɛt.li}} | *önso* "{{en: önso}}" {{say: önso = ʔøn.sɔ}} |

- It works inside a word and across words, as in *hitet mö* "{{en: hitet mö}}" {{say: hitet mö = çi.tɛp mø}}, but not across a pause (a comma or other punctuation): *önkën, po* {{say: önkën, po = ʔøŋ.kɤn pɔ}}.
- It never happens before [ʔ], so *et e* stays {{say: et e = ʔɛt ʔɛ}} and the glottal stop rule still keeps words apart.
- It does not happen before [ç]: *ethi* "{{en: ethi}}" {{say: ethi = ʔɛt.çi}}.
- Because p, m, k and ŋ never end a syllable otherwise, the listener always knows that [p] or [k] at the end of a syllable is t, and [m] or [ŋ] is n.

In a text, assimilation also happens across words.

## Not decided yet / 尚未決定

- Stress or pitch accent.
