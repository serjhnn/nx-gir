# Sources of the texts in data/

| File | Text | Source |
|------|------|--------|
| `test/grabar_john.txt` | The Gospel of John, all 21 chapters (Grabar) | Armenian Bible, Venice 1895, ed. Arsen Bagratuni, as published at <https://bible.armeniancathedral.org/book/tJn_1.htm> (chapters 1–21) (public domain) |
| `test/grabar_john_1.txt` | John 1:1–18 (Grabar) | Armenian Bible, Venice 1895, ed. Arsen Bagratuni, as published at <https://bible.armeniancathedral.org/book/tJn_1.htm> (public domain) |
| `test/grabar_hayr_mer.txt` | The Lord's Prayer, Matthew 6:9–13 (Grabar) | Armenian Bible, Venice 1895, ed. Arsen Bagratuni, as published at <https://bible.armeniancathedral.org/book/tMt_6.htm> (public domain) |
| `test/sample_english.txt` | English sample | Written for testing |

Changes made when copying the Bible texts:

- The site writes `:` and `` ` `` in place of the Armenian
  full stop and comma; they were replaced with `։` and `՝`.
- Footnote markers like `[1]` and the ``` `` ``` that
  close a footnoted passage were removed (91 in John).
  The footnotes themselves are not included.
- John 14:13 ended with two full stops around a footnote
  marker; one was kept.
- John 14:14 is not in the published text (the site
  goes from 14:13 to 14:15), so the file has 877 verses.
- Parentheses are kept as published, even where one
  opens in one verse and closes in a later one.
- One verse per line, without verse numbers. In
  `grabar_john.txt` each chapter starts with a heading
  `Գլուխ Ա` … `Գլուխ ԻԱ`.
