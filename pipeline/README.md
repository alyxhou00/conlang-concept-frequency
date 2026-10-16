# pipeline/

The scripts that turn concepts into words: `build_concept_freq.py` counts how often each concept is used, `build_lexicon.py` makes the words, `release.py` freezes a version, `render.py` turns a concept-tagged text into our language, and `find_compounds.py` drafts `mapping/compounds.tsv` (`huffman.py` and `units.py` are helpers); see [docs/A-pipeline.md](../docs/A-pipeline.md) for the order.
