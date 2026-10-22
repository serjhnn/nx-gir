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
