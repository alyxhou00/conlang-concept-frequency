"""How written words sound: letters to IPA, and the sound rules of connected speech.

The rules are described, with examples, in docs/src/01-phonology.md. Every
example there is written as {{say: words = IPA}}, and the docs build checks it
against this code; a test checks that the examples together use every rule in
RULES. So a change here that the page does not show, or an example the code
does not produce, fails the build or the tests.

The lexicon's `ipa` column is each word said on its own (pronounce([word])); a
test checks that the latest release still matches these rules.
"""
import re
import unicodedata

# /m n p t k s x ʋ ʁ l/ written m n p t k s h v r l; /i ø ɛ u ɤ ɔ ɑ/ written i ö e u ë o a
IPA = {"h": "x", "v": "ʋ", "r": "ʁ", "ö": "ø", "e": "ɛ", "ë": "ɤ", "o": "ɔ", "a": "ɑ"}
VOWELS = set("iöeuëoa")
FRONT = set("ieö")
GLOTTAL_STOP = "ʔ"
PUNCTUATION = ".,?!;:"
# next consonant -> what a coda t or n becomes before it
ASSIMILATE = {"m": {"t": "p", "n": "m"}, "p": {"t": "p", "n": "m"},
              "k": {"t": "k", "n": "ŋ"}, "x": {"t": "k", "n": "ŋ"}}

# names of the rules, as pronounce() reports them in `used`
RULES = (["glottal stop", "onset h [ç] by its own vowel", "onset h [ç] by the vowel before", "coda h [ç]", "h [x]"]
         + [f"{c} -> {new} before {nxt}" for nxt, change in ASSIMILATE.items() for c, new in change.items()]
         + ["t/n kept before [ʔ]", "t/n kept before [ç]", "t/n kept before another consonant", "t/n kept before a pause"])


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


def pronounce(words, used=None):
    """IPA of words said together without a pause, one string per word, syllables split by dots.

    If `used` is a set, the names of the rules that applied (see RULES) are added to it.
    """
    used = set() if used is None else used
    sounds = []
    for word in [syllables(w) for w in words]:
        out = []
        for i, (o, v, c) in enumerate(word):
            if o == "":
                if i == 0:
                    o = GLOTTAL_STOP
                    used.add("glottal stop")
            elif o == "h":
                before = word[i - 1][1] if i > 0 and word[i - 1][2] == "" else ""
                if v in FRONT:
                    o = "ç"
                    used.add("onset h [ç] by its own vowel")
                elif before in FRONT:
                    o = "ç"
                    used.add("onset h [ç] by the vowel before")
                else:
                    o = "x"
                    used.add("h [x]")
            else:
                o = IPA.get(o, o)
            if c == "h":
                c = "ç" if v in FRONT else "x"
                used.add("coda h [ç]" if c == "ç" else "h [x]")
            else:
                c = IPA.get(c, c)
            out.append([o, IPA.get(v, v), c])
        sounds.append(out)
    # assimilation: look at the next syllable's onset, in this word or the next
    flat = [s for word in sounds for s in word]
    for s, nxt in zip(flat, flat[1:]):
        if s[2] not in ("t", "n"):
            continue
        if nxt[0] in ASSIMILATE:
            new = ASSIMILATE[nxt[0]][s[2]]
            used.add(f"{s[2]} -> {new} before {nxt[0]}")
            s[2] = new
        elif nxt[0] in (GLOTTAL_STOP, "ç"):
            used.add(f"t/n kept before [{nxt[0]}]")
        else:
            used.add("t/n kept before another consonant")
    return [".".join("".join(s) for s in word) for word in sounds]


def speak(text, used=None):
    """IPA of written text, words split by spaces; punctuation is a pause, which stops assimilation."""
    used = set() if used is None else used
    stretches = [s.split() for s in re.split(f"[{re.escape(PUNCTUATION)}]", text)]
    stretches = [s for s in stretches if s]
    out = []
    for i, words in enumerate(stretches):
        out += pronounce(words, used)
        if i + 1 < len(stretches) and syllables(words[-1])[-1][2] in ("t", "n"):
            used.add("t/n kept before a pause")
    return " ".join(out)
