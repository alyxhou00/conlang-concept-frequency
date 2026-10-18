"""How written words sound: letters to IPA, and the sound rules of connected speech.

The lexicon's `ipa` column is each word said on its own, with these rules; in
texts they also apply across words (docs/src/01-phonology.md):

  1. A word-initial empty onset is a glottal stop [ʔ].
  2. h is [ç] next to a front vowel (i e ö) in the same word, otherwise [x]:
     hitet [çi.tɛt], utöh [ʔu.tøç], ihu [ʔi.çu].
  3. A coda t or n takes the place of the next consonant when that is a
     labial (m p) or velar (k [x]): t -> p k, n -> m ŋ. This also works across
     words, but not across a pause (punctuation), and not before [ʔ] or [ç]:
     hitet mö [çi.tɛp mø], önkën po [ʔøŋ.kɤm pɔ].
"""
import unicodedata

# /m n p t k s x ʋ ʁ l/ written m n p t k s h v r l; /i ø ɛ u ɤ ɔ ɑ/ written i ö e u ë o a
IPA = {"h": "x", "v": "ʋ", "r": "ʁ", "ö": "ø", "e": "ɛ", "ë": "ɤ", "o": "ɔ", "a": "ɑ"}
VOWELS = set("iöeuëoa")
FRONT = set("ieö")
GLOTTAL_STOP = "ʔ"
# place of the next consonant -> what a coda t or n becomes
ASSIMILATE = {"m": {"t": "p", "n": "m"}, "p": {"t": "p", "n": "m"},
              "k": {"t": "k", "n": "ŋ"}, "x": {"t": "k", "n": "ŋ"}}


def syllables(word):
    """[(onset, vowel, coda)] in letters, "" for an empty consonant: ihu -> [("", "i", ""), ("h", "u", "")]."""
    letters = list(unicodedata.normalize("NFC", word.lower()))
    out, i = [], 0
    while i < len(letters):
        onset = ""
        if letters[i] not in VOWELS:
            onset, i = letters[i], i + 1
        if i == len(letters) or letters[i] not in VOWELS:
            raise ValueError(f"{word!r} is not made of CVC syllables")
        vowel, i = letters[i], i + 1
        coda = ""
        if i < len(letters) and letters[i] not in VOWELS and (i + 1 == len(letters) or letters[i + 1] not in VOWELS):
            coda, i = letters[i], i + 1
        out.append((onset, vowel, coda))
    return out


def _h(own_vowel, other_vowel=""):
    return "ç" if own_vowel in FRONT or other_vowel in FRONT else "x"


def pronounce(words):
    """IPA of words said together without a pause, one string per word, syllables split by dots."""
    sylls = [syllables(w) for w in words]
    # onsets and codas as sounds (rules 1 and 2)
    sounds = []
    for word in sylls:
        out = []
        for i, (o, v, c) in enumerate(word):
            if o == "":
                o = GLOTTAL_STOP if i == 0 else ""
            elif o == "h":
                before = word[i - 1][1] if i > 0 and word[i - 1][2] == "" else ""
                o = _h(v, before)
            else:
                o = IPA.get(o, o)
            c = _h(v) if c == "h" else IPA.get(c, c)
            out.append([o, IPA.get(v, v), c])
        sounds.append(out)
    # rule 3: look at the next syllable's onset, in this word or the next
    flat = [s for word in sounds for s in word]
    for s, nxt in zip(flat, flat[1:]):
        s[2] = ASSIMILATE.get(nxt[0], {}).get(s[2], s[2])
    return [".".join("".join(s) for s in word) for word in sounds]
