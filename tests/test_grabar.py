import nxgir_grabar as grabar

TABLE = grabar.load()


def test_table_is_well_formed():
    assert len(TABLE) > 100
    for a in TABLE:
        assert a.kind in grabar.KINDS
        assert a.short and a.full and a.meaning
        assert set(a.sources) <= set(grabar.SOURCES)
        assert "՟" not in a.short
    pairs = [(a.short, a.full) for a in TABLE]
    assert len(pairs) == len(set(pairs))


def test_expand_sacred_names_any_case_or_mark():
    for word in ("ած", "ԱԾ", "Ա՟Ծ", "ա՟ծ"):
        fulls = [f for f, _ in grabar.expand(word, TABLE)]
        assert fulls == ["Աստուած"]
    assert grabar.expand("տն", TABLE)[0][0] == "տեառն"


def test_expand_gives_every_reading():
    fulls = [f for f, _ in grabar.expand("վրդ", TABLE)]
    assert fulls == ["վարդապետ", "Վարդան"]


def test_expand_endings():
    def full(word):
        return grabar.expand(word, TABLE)[0][0]

    assert full("գիտութի") == "գիտութիւն"
    assert full("բնւի") == "բնութիւն"
    assert full("քաջութե") == "քաջութեան"
    assert full("քաջւեն") == "քաջութեանն"
    assert full("քաջւեբ") == "քաջութեամբ"


def test_examples():
    ((full, a),) = grabar.expand("ա՟մցն", TABLE)
    assert full == "ամենեցուն"
    assert a.sources == ("N",)
    assert a.examples()[0] == (
        "տէր ամենեցուն",
        "Lord of all",
    )
    assert grabar.example_lines(a)[0] == (
        '  e.g. տէր ամենեցուն: "Lord of all"'
    )
    assert grabar.expand("ամ", TABLE)[0][1].example == ""


def test_expand_unknown():
    assert grabar.expand("բան", TABLE) == []
    # an ending alone is not a word
    assert grabar.expand("ութի", TABLE) == []


def test_expand_prefix():
    def fulls(word):
        return [
            (h.full, h.prefix)
            for h in grabar.expand_prefix(word, TABLE)
        ]

    assert fulls("յա՟մ") == [("յամենայն", "յ")]
    assert fulls("զամ") == [("զամենայն", "զ")]
    assert fulls("ցած") == [("ցԱստուած", "ց")]
    assert fulls("իվ՟ր") == [("ի վերայ", "ի")]
    assert fulls("իքս") == [("ի Քրիստոս", "ի")]
    # յ is not written before a consonant, ի before
    # a vowel
    assert fulls("յսբ") == []
    assert fulls("իամ") == []
    # a whole entry starting with ի is not split
    assert grabar.expand("իղի", TABLE)
    # a one-letter rest matches too much
    assert fulls("զգ") == []
    assert grabar.expand("յամ", TABLE) == []


def test_search():
    shorts = [
        a.short for a in grabar.search("bishop", TABLE)
    ]
    assert shorts == ["եպկս"]
    assert grabar.search("Կաթողիկոս", TABLE)


def test_lines_fit_a_phone():
    out = grabar.lines(TABLE, width=40)
    assert out[0] == grabar.KINDS["sacred"]
    assert "  ած   Աստուած  · God" in out
    wrapped = [
        line
        for line in out
        if "  " in line.strip() and len(line) >= 40
    ]
    # only rows whose two forms alone are wider
    for line in wrapped:
        assert "·" not in line


def test_explain():
    out = grabar.explain("ա՟ծ", TABLE)
    assert out[:2] == ["ա՟ծ → Աստուած", "  God"]
    out = grabar.explain("յա՟մ", TABLE)
    assert out[0] == "յա՟մ → յամենայն"
    assert out[1].startswith("  յ- ")
    assert grabar.explain("բառ", TABLE) == []


def small_vocab(tmp_path):
    words = tmp_path / "vocabulary.tsv"
    words.write_text(
        "# test\n"
        "լուսին\tnoun\tmoon | month\n"
        "եւ\tconj\tand\n"
        "ես\tpron\tI\n"
        "ես\tverb\tyou are\n",
        encoding="utf-8",
    )
    forms = tmp_path / "forms.tsv"
    forms.write_text(
        "# test\nլուսնի\tլուսին\n", encoding="utf-8"
    )
    return grabar.vocabulary(words, forms)


def test_vocabulary_files_are_well_formed():
    for path, cols in (
        (grabar.VOCABULARY, 3),
        (grabar.FORMS, 2),
    ):
        for row in grabar.tsv(path):
            assert len(row) == cols and all(row), row
    heads, forms = grabar.vocabulary()
    for words in forms.values():
        for w in words:
            assert grabar.key(w) in heads, w


def test_lookup(tmp_path):
    vocab = small_vocab(tmp_path)

    def heads(word):
        return [
            (w.word, notes)
            for w, notes in grabar.lookup(word, vocab)
        ]

    assert heads("Լուսին") == [("լուսին", ())]
    # an inflected form
    assert heads("լուսնի") == [("լուսին", ())]
    # every entry of a word
    assert [w for w, _ in heads("ես")] == ["ես", "ես"]
    # the ligature և is եւ
    assert heads("և") == [("եւ", ())]
    # a joined preposition and the article
    (w, notes), *_ = heads("զլուսինն")
    assert w == "լուսին"
    assert notes[0].startswith("զ- ")
    assert notes[1].startswith("-ն ")
    assert heads("բառ") == []


def test_define(tmp_path):
    vocab = small_vocab(tmp_path)
    out = grabar.define("լուսնի", vocab)
    assert out[:3] == ["լուսին · noun", "  moon", "  month"]
    assert out[-1].startswith("Source: Wiktionary")
    out = grabar.define("զլուսին", vocab)
    assert "զլուսին:" in out
    assert grabar.define("բառ", vocab) == []


def test_define_real_words():
    out = grabar.define("սիրեաց")
    assert out[0] == "սիրեմ · verb"
    out = grabar.define("յերկինս")
    assert "երկինք · noun" in out
