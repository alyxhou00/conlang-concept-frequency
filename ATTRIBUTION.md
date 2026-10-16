# Attribution and licenses

Data and software this project uses, with the attribution statement each license asks for. Full citations are in [REFERENCES.md](REFERENCES.md).

This repository does not redistribute any of the datasets below: `data/` and the generated tables in `out/` are not committed. `checks/check_sources_output.txt` quotes a handful of individual values from them as part of the analysis.

## Data (Creative Commons)

### Concepticon: CC BY 4.0

- **What we use:** `concepticon-data` at commit `a89063d` (2026-08-27): the concept sets, the word columns of the concept lists, and the concept list `Calude-2011-200`. `mapping/merges.tsv` and `mapping/compounds.tsv` in this repository contain Concepticon concept IDs and glosses, so the statement below applies to them.
- **License:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (stated in `concepticon-data/metadata.json`).
- **Statement:**
  > Concept lists and concept sets from Concepticon (List et al. 2026, version 3.4.0, https://concepticon.clld.org), licensed under CC BY 4.0. The Calude-2011-200 list is based on Calude & Pagel (2011).

### NoRaRe: CC BY-NC 4.0 (non-commercial)

- **What we use:** `norare-data` at commit `4b8901d` (2026-10-07). This includes the frequency datasets Brysbaert-2009, Brysbaert-2011, Cai-2010, Cuetos-2011, Dimitropoulou-2010, Keuleers-2010, Mandera-2015, Crepaldi-2015, the Wu-2020 core vocabulary, and Bond-2013-OMW (the link from concepts to WordNet synsets that we use to find Japanese words). For root families (goal 2) we also use List-2023-Colexifications, Zalizniak-2024-DatSemShift and Rubehn-2025-ConceptEmbeddings.
- **License:** [Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/) (the `LICENSE` file in `norare-data`).
- **Statement:**
  > Word frequencies and norms mapped to Concepticon from NoRaRe (Tjuka, Forkel & List 2022, https://norare.clld.org), licensed under CC BY-NC 4.0. Original datasets: Brysbaert & New (2009); Brysbaert et al. (2011); Cai & Brysbaert (2010); Cuetos et al. (2011); Dimitropoulou et al. (2010); Keuleers et al. (2010); Mandera et al. (2015); Crepaldi et al. (2015); Wu, Nicolai & Yarowsky (2020); Bond & Foster (2013); List (2023); Zalizniak et al. (2024, Database of Semantic Shifts); Rubehn & List (2025).
- **Note:** anything derived from NoRaRe can't be used commercially.

### wordfreq data: CC BY-SA 4.0 (share-alike)

- **What we use:** the word lists bundled with `wordfreq` 3.1.1. We look up words through the library and don't export the lists.
- **License:** the code is Apache 2.0; the data files are [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The data comes from Wikipedia, subtitles (OpenSubtitles, SUBTLEX), news, books (Google Books Ngrams), the web, Twitter and Reddit. The SUBTLEX lists are included with Marc Brysbaert's permission, under terms similar to CC BY-SA. Details are in the wordfreq README.
- **Statement:**
  > Word frequencies from wordfreq (Speer 2022, https://github.com/rspeer/wordfreq), whose data is licensed under CC BY-SA 4.0.
- **Note:** a frequency table we publish that is derived from wordfreq has to be released under CC BY-SA 4.0. The author also asks people not to redistribute the data as CSV dumps.

## Data (other licenses)

### Japanese WordNet: NICT license (permissive, notice required)

- **What we use:** the Japanese lemmas in `omw-1.4/jpn/wn-data-jpn.tab` from the Open Multilingual Wordnet 1.4 zip (`data/omw-1.4.zip`). `freq/build_concept_freq.py` uses them to find a Japanese word for each concept.
- **License:** use, copying, modification and distribution are allowed for any purpose, as long as the copyright notice, statements and disclaimer appear on all copies, including modified ones (the `omw-1.4/jpn/LICENSE` file).
- **Required notice** (must accompany anything we distribute that contains Japanese WordNet data, such as `out/concept_freq_by_lang.tsv`):
  > Japanese WordNet Copyright 2009 by the National Institute of Information and Communications Technology (NICT). All rights reserved.
  >
  > THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND NICT MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, NICT MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS.
  >
  > The name of the National Institute of Information and Communications Technology may not be used in advertising or publicity pertaining to distribution of the software and/or database. Title to copyright in this software, database and any associated documentation shall at all times remain with National Institute of Information and Communications Technology and LICENSEE agrees to preserve same.
- **Cite:** Isahara et al. (2008); Bond & Foster (2013) for the Open Multilingual Wordnet.

### Open question: combining sources

If we publish one combined concept-frequency table, its license depends on which sources went into it. NoRaRe (NC) and wordfreq (SA) don't combine cleanly: share-alike requires the same license, and NC adds a restriction that CC BY-SA doesn't allow. Before publishing a combined table, we should either pick sources whose licenses are compatible or ask the dataset authors. (This is a reading of the license terms, not legal advice.)

## Software

| Package | Version | License |
| --- | --- | --- |
| wordfreq | 3.1.1 | Apache 2.0 (code); data CC BY-SA 4.0 |
| pysem | 1.3.0 | MIT |
| pyconcepticon | 4.0.0 | Apache 2.0 |
| pynorare | 1.1.0 | Apache 2.0 |
| pybtex | 0.26.1 | MIT |
| pandas | 3.0.6 | BSD 3-Clause |
| jieba (via wordfreq[cjk]) | 0.42.1 | MIT |
| mecab-python3 (via wordfreq[cjk]) | 1.0.12 | BSD |
| pytest | 9.1.1 | MIT |

## Not used yet

The discussion doc also mentions OPUS, WOLD, Lexibank and CLICS⁴. Their licenses haven't been checked yet. Add them here when we start using them.
