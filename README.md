# conlang-concept-frequency

We want to create a constructed language (conlang) in which the concepts people use most often get the shortest words, so we estimate how often each concept is used across many languages and then assign word lengths with Huffman coding.

The plan and our discussion are in [人造語言：跨語言概念頻率與編碼.md](人造語言：跨語言概念頻率與編碼.md).

## Setup

Python 3.13.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

The data repositories are not committed here. Clone them into `data/` at the commits we used:

```bash
git clone https://github.com/concepticon/concepticon-data.git data/concepticon-data
git -C data/concepticon-data checkout a89063d5657022a4ac11c557baef4958809e7c91
git clone https://github.com/concepticon/norare-data.git data/norare-data
git -C data/norare-data checkout 4b8901d6fa3d6cc14afbde6bf2fb061d4a4ab2c4
```

## Layout

| Path | Contents |
| --- | --- |
| `data/` | Concepticon and NoRaRe clones (not committed) |
| `checks/check_sources.py` | Sanity checks on Calude-2011-200, NoRaRe and wordfreq |
| `checks/check_sources_output.txt` | Output of the last run |
| `ATTRIBUTION.md` | Licenses and attribution statements for the data we use |
| `REFERENCES.md` | Literature (參考文獻) |

Planned (from the discussion doc): `mapping/`, `freq/`, `encode/`, `notebooks/`.

## Running the checks

```bash
.venv/Scripts/python -X utf8 checks/check_sources.py
```

`-X utf8` is needed on Windows consoles that are not set to UTF-8.

## Licenses

Our data sources have different licenses, and NoRaRe is **non-commercial only** (CC BY-NC 4.0). See [ATTRIBUTION.md](ATTRIBUTION.md) before redistributing any derived frequency tables. No license has been chosen yet for this repository's own code.
