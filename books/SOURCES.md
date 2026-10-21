# Sources of the books in books/

## grabar/bible/new-testament/

The four Gospels in Grabar, from the Armenian Bible,
Venice 1895, edited by Arsen Bagratuni (public domain),
as published at <https://bible.armeniancathedral.org/>.

| File | Book | Chapters | Verses |
|------|------|---------:|-------:|
| `1-matthew.txt` | Աւետարան ըստ Մատթէոսի | 28 | 1068 |
| `2-mark.txt` | Աւետարան ըստ Մարկոսի | 16 | 675 |
| `3-luke.txt` | Աւետարան ըստ Ղուկասու | 24 | 1153 |
| `4-john.txt` | Աւետարան ըստ Յովհաննու | 21 | 877 |

Downloaded with `scripts/fetch-bible.py`, which also
documents the cleanup:

```sh
D=books/grabar/bible/new-testament
scripts/fetch-bible.py Mt 28 "Աւետարան ըստ Մատթէոսի" $D/1-matthew.txt
scripts/fetch-bible.py Mk 16 "Աւետարան ըստ Մարկոսի" $D/2-mark.txt
scripts/fetch-bible.py Lk 24 "Աւետարան ըստ Ղուկասու" $D/3-luke.txt
scripts/fetch-bible.py Jn 21 "Աւետարան ըստ Յովհաննու" $D/4-john.txt
```

Changes made when copying:

- The site writes `:` and `` ` `` in place of the Armenian
  full stop and comma; they were replaced with `։` and `՝`.
- Footnote markers like `[12]` and the ``` `` ``` that
  close a footnoted passage were removed (107 in Matthew,
  110 in Mark, 151 in Luke, 91 in John). The footnotes
  themselves are not included.
- Where a full stop stood on both sides of a footnote
  marker, one was kept (Matthew 1×, Mark 2×, John 1×).
- One verse per line, without verse numbers; each
  chapter starts with a heading `Գլուխ Ա`, `Գլուխ Բ`, ….

How this edition differs from the usual verse list:

- Matthew 16:3 has a number but no text, and Matthew
  23:14 is not in the edition. Both passages are also
  missing from several old manuscripts.
- Mark 9 numbers its verses 42, 44, 46 where other
  editions use 43–47; the text (hand, foot, eye) is all
  there.
- Luke has 1153 verses against the usual 1151 because
  of different verse division.
- John 14:14 is not in the edition.

## grabar/grigor-tatevatsi/

Three works of Grigor Tatevatsi (Գրիգոր Տաթեւացի,
1346–1409) in Grabar, from Digilib, the digital library
of Armenian literature of the American University of
Armenia (<https://www.digilib.am>). Digilib typed the
texts from old printed editions; the texts themselves
are centuries old and in the public domain. Digilib
does not state a license for its typed copies.

| Folder | Work | Digilib | Sections | Parts |
|--------|------|---------|---------:|------:|
| `1-girk-harcmanc/` | Գիրք հարցմանց (Book of Questions) | [1477](https://www.digilib.am/book/1477/) | 511 | 12 |
| `2-dzmeran-hator/` | Գիրք քարոզութեան որ կոչի Ձմեռան հատոր (winter sermons) | [1476](https://www.digilib.am/book/1476/) | 164 | 18 |
| `3-amaran-hator/` | Գիրք քարոզութեան որ կոչի Ամառան հատոր (summer sermons) | [3409](https://www.digilib.am/book/3409/) | 38 | 24 |

Downloaded on 2026-10-21 with `scripts/fetch-digilib.py`:

```sh
D=books/grabar/grigor-tatevatsi
scripts/fetch-digilib.py 1477 "Գիրք հարցմանց" $D/1-girk-harcmanc
scripts/fetch-digilib.py 1476 "Գիրք քարոզութեան որ կոչի Ձմեռան հատոր" $D/2-dzmeran-hator
scripts/fetch-digilib.py 3409 "Գիրք քարոզութեան որ կոչի Ամառան հատոր" $D/3-amaran-hator
```

How the files are made:

- Each Digilib section becomes a heading line followed
  by its paragraphs, one per line. Runs of spaces
  become one space, and a heading repeated as the
  first paragraph is kept once; otherwise spelling,
  punctuation and the stress marks (՛) are as on
  Digilib.
- Each work is cut into parts of about 150,000
  characters (`01.txt`, `02.txt`, …) between sections,
  so the reader stays quick on a phone. The first line
  of a part is the title and `n/total`.
- In Գիրք հարցմանց, 42 sections are only group headings
  (e.g. `Գլուխ Ա ի մեծ ցանկէն`, `Երկրորդ Հատոր`) and
  have no text of their own.
- Some paragraphs are very long (a whole sermon in the
  summer volume can be one paragraph), as on Digilib.
