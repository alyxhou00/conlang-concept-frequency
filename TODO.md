# To-do / 待辦

Ordered by what depends on what. Details for most items are in the discussion doc ([人造語言：跨語言概念頻率與編碼.md](人造語言：跨語言概念頻率與編碼.md)). Tick an item off (`[x]`) when it is done and committed.

**Working in parallel:** all sessions share this folder, because `.venv/` and `data/` are not in git.

- Tasks that rebuild `out/` (items 3 and 4) must run **one after the other**; otherwise they overwrite each other's output and report wrong statistics.
- Shared files (the discussion doc, this file) are changed with small targeted edits only.

## Now / 現在

- [ ] **Review and commit the coverage check.** Not committed yet:
  - the report (section 〈常用詞涵蓋檢查（2026-10-16）〉)
  - four new texts in `texts/`
  - changes to `ATTRIBUTION.md`, `.gitignore` and `README.md`
- [ ] **Push to GitHub** (you): `gh repo create conlang-concept-frequency --private --source=. --remote=origin --push`
- [ ] **Clean up the repo** (you, after the intensive vibe-coding phase): read through the code, docs and the discussion doc; remove what's no longer needed, merge duplicates, and make the structure easy to follow.

## Before 0.2.0 / 下一個 beta 之前

1. [ ] **Concept-tag the full UDHR** (preamble and 30 articles) as `texts/udhr-full.txt`. *(task card from the coverage session)* Do this first: it shows which grammar and concepts the text really needs.
2. [ ] **Grammar decisions, round 2.** *(task card)* After item 1. The test texts can't be rendered until these are decided; they are marked `?REL`, `?FUT` … in `texts/`.
   - Tense and aspect.
   - Relative clauses.
   - Comparison.
   - Clause linking.
   - Modals: is *shall* SHOULD or MUST?
   - Focus particles.
   - Imperative and wishes.
   - Interjections.
   - Where BY (PASSIVE MARKER) goes.
   - any / none.
   - Order of two objects.
   - Locations as predicates.
   - **Can a verb be used as a noun directly (轉類)?**
3. [ ] **Fix inflated frequencies.** *(task card from the coverage session)* Covers:
   - NoRaRe mappings that give rare concepts a common word's frequency: OF THIS KIND (SUCH) ← "so", rank 30.
   - Values filled from wordfreq: Spanish *era* for THRESHING-FLOOR, which is also "was".
   - Our own particles: PAST (PARTICLE) ← 了, rank 5.
4. [ ] **Add the missing concepts.** *(task card)* After items 2 and 3.
   - Which of the 118 proposed concepts to add, merge, or say with existing words.
   - The ID scheme: 900007–900124 collides with the particles at 900101–900103.
   - Whether INTERNET, VIDEO and EMAIL get their own words.
   - The particles decided in item 2.
   - Fix any texts that used a proposed gloss that changed.
5. [ ] **Make THOU / YOU unmistakable.** *(task card)* Can run any time.
   - THOU (1215) = "you, one person" = *a*; YOU (1213) = "you, several people" = *së*. People writing English will write YOU and mean one person.
   - The planned NAME particle needs a label that can't be confused with the noun NAME.
6. [ ] **Names list and the NAME particle.**
   - Add the NAME particle.
   - `mapping/names.tsv`, starting with SHORT LANGUAGE, with `@KEY` references in texts and docs.
   - The rules for adapting foreign sounds.
   - How foreign names are spelled.
   - Whether country and language names are translated or transcribed.
7. [ ] **Release 0.2.0** and rebuild the docs (see [docs/A-pipeline.md](docs/A-pipeline.md)). Add a test that every text in `texts/` renders.

## Before 1.0.0 / 凍結 v1 之前

8. [ ] **Number system**: numbers above ten, ordinals. The coverage report lists the number words.
9. [ ] **Root families** (goal 2): related concepts share a root. This changes many words, so it must happen before 1.0.0.
10. [ ] **More texts**: The Wonderful Wizard of Oz, the full North Wind and the Sun.
11. [ ] **Dictionary webpage.** The word list (`lexicon/<version>.tsv`) can be published; only the frequencies can't. A page makes it usable:
    - Search both ways: concept or English → our word, and our word → meaning.
    - Each concept with its Concepticon definition (CC BY, with attribution).
    - IPA, syllables, and how merged concepts and compounds are said; the names list once it exists.
    - Generated from each release by a script, like `docs/`, as one static HTML page.
    - Where to host it: GitHub Pages needs a public repo or a paid plan for private ones; otherwise share the page some other way.
12. [ ] **Small open points**: language code; stress or pitch accent; capitalization at sentence start.
13. [ ] **Release 1.0.0.** From then on, existing words never change.
