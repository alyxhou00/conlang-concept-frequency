import pytest

import build_docs


@pytest.fixture(scope="module")
def builder():
    return build_docs.Builder(build_docs.versions()[-1])


def fill(builder, template):
    return builder.fill(template, "x.md").split("\n", 1)[1]  # without the header comment


def test_meaning_of_fixed_words(builder):
    assert fill(builder, "{{en: hitet}}") == "dispute"
    assert fill(builder, "{{en: hitet mö}}") == "dispute + past (particle)"
    assert fill(builder, "{{en: inat po}}") == "result in"  # a compound
    assert fill(builder, "{{en: ö}}") == "I"


def test_meaning_fails_for_a_word_that_is_gone(builder):
    with pytest.raises(ValueError, match="zzz: not a word in lexicon"):
        fill(builder, "{{en: hitet zzz}}")


def test_say_checks_the_ipa_written_on_the_page(builder):
    assert fill(builder, "{{say: hitet mö = çi.tɛp mø}}") == "[çi.tɛp mø]"
    with pytest.raises(ValueError, match="the sound rules say 'hitet mö' is"):
        fill(builder, "{{say: hitet mö = xi.tɛt mø}}")
    with pytest.raises(ValueError, match="so the example is checked"):
        fill(builder, "{{say: hitet mö}}")


def test_docs_src_do_not_name_a_lexicon_version():
    # write {{version}} instead, so the pages never point at an old version;
    # A-pipeline.md is exempt, its numbers are examples of the numbering scheme
    for src in sorted(build_docs.SRC.glob("*.md")):
        if src.name == "A-pipeline.md":
            continue
        text = src.read_text(encoding="utf-8")
        named = [v for v in build_docs.versions() if v in text]
        assert not named, f"docs/src/{src.name} names lexicon version {', '.join(named)}"
