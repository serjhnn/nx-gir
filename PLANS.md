# nx-gir: long-term plans

A place for ideas and plans. This project will keep
growing for years, so this file is a living document:
add, change, and cross out as the ideas develop.

## The vision

Bring old Armenian manuscripts together on one online
platform, and make them open to anyone who is
interested, including people who don't know Armenian or
Grabar.

The Matenadaran alone holds tens of thousands of
manuscripts, and many of them have not been opened for
centuries. Their texts, pictures, and ornaments should
not stay hidden on shelves. They should be readable,
searchable, and seen.

## Three collections

### 1. Manuscripts library

- Collect the manuscripts in one place, starting with
  the Matenadaran and later other collections around the
  Armenian world
- For every manuscript: page scans, the text (via OCR
  and Grabar tools), and a description (title, author or
  scribe, date, place, size, condition)
- Make them readable for everyone:
  - original Grabar text
  - modern Armenian spelling
  - transliteration into Latin letters
  - translations or summaries in other languages
  - glossary help for old words and abbreviations
- Search by title, author, scribe, place, century,
  subject, and full text

### 2. Picture library

- Collect the pictures these books contain: miniatures,
  illuminated headpieces, decorated initials, marginal
  drawings
- Each picture is linked back to its manuscript and page
- Browse and search by subject, color, style, painter,
  school, period, and place

### 3. Knots

- Collect ancient Armenian knots and interlace
  ornaments from all around the Armenian world: from
  manuscripts, khachkars, churches, carpets, and other
  sources
- For every knot: a picture, where and when it was
  found, the source, and a clean drawing of the pattern
- Over time, compare and group them: how a pattern
  travels and changes between regions and centuries

## How nx-gir fits in

The terminal reader is the first building block. The
tools made for it are the same tools the platform needs:

- OCR for scanned pages → turning manuscript scans into
  text
- Grabar helpers (abbreviations, modern spelling,
  transliteration, numerals, glossary) → making the text
  readable for people who don't know Grabar

## Rough stages

1. **Interactive reader.** A terminal app for reading a
   book and understanding unknown words (details below).
   OCR and other Grabar helpers grow around it.
2. **First collection.** A small set of manuscripts
   (scans, text, descriptions) in one simple data format.
3. **Online platform.** A website to browse, read, and
   search the collection.
4. **Picture library.** Add miniatures and ornaments,
   linked to their pages.
5. **Knots.** Start the knot collection.
6. **Growing.** More manuscripts, more collections,
   translations, and help from volunteers and experts.

## Stage 1: interactive reader

A terminal reader that helps with words you don't know.

How it works:

1. Open a book and read it page by page.
2. Move the cursor to a word you want to know more about.
3. Press a key to get information about that word:

| Key | Shows |
|-----|-------|
| `t` | **Translation**: the word's meaning in modern Armenian (later other languages too) |
| `e` | **Explanation**: dictionary form, grammar (case, number, tense), and notes on old words and abbreviations |
| `s` | **References**: other places in the book where the word appears, so you can jump to them |

The information shows in a panel next to or below the
text, and the reader keeps your place in the book.

Progress:

- [x] Reader screen that fits the window, paging
- [x] Word cursor (`w`/`b`, `j`/`k`, `0`/`$`, `g`/`G`)
- [x] `s`: references panel (same word form for now)
- [x] Panel beside the text on wide screens (`p` to
      choose: auto, below, beside)
- [x] Remember the last position, bookmarks (`m`,
      `M`), settings and reading progress
- [x] Notes on sentences (`O` adds, `o` lists, `•`
      marks a sentence with notes; `nxgir notes`
      prints them)
- [ ] `t` and `e` with a starter glossary
- [ ] `s` across different forms of the same word

What it needs:

- A reader screen: paging, moving between words,
  bookmarks, remembering the last position
- A Grabar dictionary to look words up in (starter
  glossary first, larger dictionaries later)
- Finding the dictionary form of a word: Grabar words
  change their endings (`-ոյ`, `-աց`, `-ոց`, `-աւ`,
  `-ս`, `-դ`, `-ն`, …), so the reader needs to strip them
  to find the word
- An index of every word in the book for `s`, matching
  different forms of the same word

## Plan: pictures of places with their locations

Collect many pictures of places (churches, khachkars,
monasteries, inscriptions, carved knots) together with
where they are, for the picture library and the knots.
Google Maps is the starting point for finding places.

The rule from Google: the Maps terms do not allow
scraping, bulk downloading, or keeping Google's photos
and map data in our own collection. Photos from the
Places API may only be shown live, with their author
credits, not saved. So Google Maps is used to *find*
places; the pictures we keep come from sources that
allow it.

Where the pictures come from:

- Our own photos, and photos people send us with
  permission; the GPS location is read from the photo
  (EXIF)
- Our own Google Maps photos and saved places, through
  Google Takeout (they are ours to keep)
- Wikimedia Commons: many geotagged photos of Armenian
  churches and khachkars, under free licenses
- Wikidata: places with coordinates and a picture
  (for example "instance of: khachkar" or "church
  building" in Armenia and Artsakh)
- Mapillary: street-level photos under CC BY-SA
- Flickr: only photos with a free license and a
  location
- Monument lists (the Armenian state list of
  monuments, Wiki Loves Monuments Armenia) for the
  names and ids of places

For every picture we keep:

- the file, and a small preview
- place name (Armenian and Latin), latitude and
  longitude, and how exact the location is
- what it shows (church, khachkar, knot, inscription)
- the source, link, author, license and date
- the place id in the monument list or Wikidata, if
  there is one

TODO:

- [ ] Choose the data format: a `places.tsv` and a
      `pictures.tsv`, the pictures in a folder by
      place
- [ ] Find the places: a list made by hand in Google
      Maps (saved list → Takeout), plus the monument
      lists and Wikidata
- [ ] A script to read our own photos: GPS and date
      from EXIF, matched to the nearest known place
- [ ] A script to fetch Wikimedia Commons pictures by
      category or by area, with their licenses
- [ ] A script to fetch Wikidata places with
      coordinates and pictures (SPARQL)
- [ ] Mapillary and Flickr, after the first two work
- [ ] Find and drop duplicates (same picture from two
      sources)
- [ ] Check every license; keep only free ones, and
      keep the credits with the picture
- [ ] A map view to see what is collected and where
      the gaps are
- [ ] Decide where the pictures are stored (they will
      not fit in git; see the hosting question below)

## Plan: Armenian meanings of words (`A`)

`a` in the reader shows what a word means in English
(the Old Armenian entries of the English Wiktionary).
`A` shows the meaning in Armenian (done: built by
`scripts/fetch-vocabulary-hy.py` into
`grabar/vocabulary-hy.tsv`).

Chosen source: the Armenian Wiktionary
(hy.wiktionary.org), from its dump on
dumps.wikimedia.org (CC BY-SA 4.0, like the English
data). kaikki.org has no extract of it, so we read the
dump ourselves. What we found (dump of 2026-10-01):

- There is no Grabar section: the entries are modern
  Armenian, in the reformed spelling. Many give the
  classical spelling in `{{why|աստուած}}`, and old
  senses are marked `{{հնց}}` (about 7,500) or
  `{{գրբ}}`.
- 3,982 of our 7,679 Grabar headwords match an entry
  by title or by `{{why}}`; with simple spelling rules
  (իւ → յու, եա → յա, է → ե, -եմ → -ել, -ամ → -ալ, …)
  it was about 4,800 (62%) in the first count; in
  the built file it is 4,565 of 7,702 (59%).
- In the books in `books/`, 81% of the words get an
  English meaning; 75% get an Armenian one (71% from
  our headwords, the rest from the classical spellings
  of entries that have no English Grabar entry).
- The meanings are modern Armenian senses, not always
  the Grabar one; the `{{հնց}}` senses come closest.

Other sources, not used now; for later:

- [ ] *Նոր բառգիրք հայկազեան լեզուի* (Venice,
      1836–37): the great Grabar dictionary, public
      domain. Its explanations are in Grabar (and
      Latin), and it exists only as scans, so it needs
      OCR of two-column old print
- [ ] Հ. Աճառյան, *Հայերեն արմատական բառարան*
      (1926–35): public domain since 2024 (the author
      died in 1953). Roots and their history, with
      Armenian explanations; scans only, needs OCR
- [ ] Ստ. Մալխասյանց, *Հայերէն բացատրական բառարան*
      (1944–45): Grabar and modern words explained in
      Armenian, the best fit. Under copyright until the
      end of 2027 (the author died in 1957); free from
      2028
- [ ] Online copies of these dictionaries (e.g.
      nayiri.com): check their terms before using any
      text from them; copy only from scans we can cite
- [ ] Follow «տե՛ս [[...]]» (see …) links in the
      Wiktionary entries one step, to the entry that
      has the meaning
- [ ] Better old → new spelling rules, tested on the
      words that are still not found
- [ ] Show which senses are old (`{{հնց}}`, `{{գրբ}}`)
      first, or only those

## Plan: Claude's meanings for the rest

`grabar/vocabulary-claude.tsv` has meanings written
by Claude (English and Armenian, one line per word
form) for the words of `books/grabar/` that the
Wiktionary lists lack. Shown only when Wiktionary has
nothing, always marked as written by an AI.

Done (2026-11-07): the 889 most frequent of these
forms. Words with a meaning in the books went from
84.9% to 91.5%.

What is left: about 46,000 forms, most of them rare
(30,000 appear only once). Counted on 2026-11-07:

| Forms glossed | Words with a meaning |
|--------------:|---------------------:|
| 900 (now) | 91.5% |
| 2,000 | about 92.7% |
| 5,000 | about 94.8% |
| 10,000 | about 96.3% |
| 20,000 | about 97.7% |

How each batch is made:

1. List the missing forms, most frequent first
   (every word of `books/grabar/` that neither
   Wiktionary list nor the file has).
2. Write about 300 lines: form, headword, pos,
   English, Armenian (reformed spelling).
3. Leave out forms that cannot be read with
   confidence (fragments, typing slips).
4. Letter numbers by their real values (ա 1 … թ 9,
   ժ 10 … ղ 90, ճ 100 … ջ 900, ռ 1000 … ք 9000).
5. Run the tests, measure the coverage again,
   commit.

TODO:

- [ ] Batches up to 2,000 forms
- [ ] Batches up to 5,000 forms
- [ ] Then by book: the forms of one book at a time
      (the Shnorhali poems lack the most: 23–33% of
      their words), so a book reads fully
- [ ] A script that lists the missing forms (now a
      one-off in the session), with their count and
      one example sentence each, so a form is glossed
      in context
- [ ] Recheck the most frequent lines with their
      sentences; a form with two readings gets both
- [ ] When the Wiktionary lists are built again, drop
      the lines Wiktionary now has (a test fails on
      them)
- [ ] Ask someone who reads Grabar to check a sample;
      note in the file which lines were checked
- [ ] New books (the Digilib authors): add their
      missing frequent forms after each download

## Plan: Grigor Tatevatsi in modern Armenian

Translate the three works of Grigor Tatevatsi in
`books/grabar/grigor-tatevatsi/` into modern Eastern
Armenian, one sentence per line, to read side by
side with the Grabar in the web reader.

What there is (from Digilib, see `books/SOURCES.md`):

| Work | Parts | Size |
|------|------:|-----:|
| `1-girk-harcmanc/` Գիրք հարցմանց | 12 | 3.0 MB |
| `2-dzmeran-hator/` Ձմեռան հատոր | 18 | 4.6 MB |
| `3-amaran-hator/` Ամառան հատոր | 24 | 4.8 MB |

54 parts, about 6 million letters; a part is about
230 KB (115,000 letters). Part 1 of Ամառան հատոր is
done (2026-11-06): 1,201 sentences, both files line
for line.

What part 1 taught us:

- Translating whole paragraphs first and cutting
  them into sentences afterwards was the hard part:
  the translation joined what the Grabar says in two
  sentences (mostly `որ ասէ։ (quotation)`), and the
  two had to be matched up again by hand.
- So: **cut the Grabar into sentences first, then
  translate it line by line**. Each line of the
  translation is then the translation of the same
  line of the Grabar, and nothing has to be matched.
- A sentence ends at `։` (and `:`), as the reader's
  `sentence_starts()` counts it, also when `)`
  follows (`։)`). The Grabar `.` is a pause inside a
  sentence, not an end.
- Some Digilib slips are in the text (a missing space
  after `։`, repeated passages, typos); keep them in
  the Grabar and translate what stands there.

How each part is done:

1. Cut the Grabar part into sentences with the
   script (below): one sentence per line, a blank
   line where a Digilib paragraph ended. The words
   stay as they are; check it with the script's
   test (same text, spaces aside).
2. Translate it line by line into
   `books/ashkharhabar/grigor-tatevatsi/<work>/NN.txt`:
   the same number of lines, blank lines in the same
   places. The first line is the title
   (`Քարոզգիրք, որ կոչվում է … · n/total`).
3. Check: the test (below) passes; spot-read the
   two side by side in `nxgir web`.
4. Add the part to `books/SOURCES.md` (a line in the
   table under `ashkharhabar/grigor-tatevatsi/`).
5. Commit per part, so a long work can stop and go
   on at any part.

How the translation is written:

- Reformed (Soviet) spelling, as in Armenia today.
- Close to the Grabar, sentence by sentence; clear
  modern words, not a retelling. Quotations keep the
  Grabar's parentheses.
- Bible quotations are translated from the Grabar
  as they stand (Tatevatsi often quotes from memory);
  the 1994 Etchmiadzin translation is not copied (it
  is not free).
- The same Grabar term gets the same modern word
  everywhere: keep a list in
  `books/ashkharhabar/grigor-tatevatsi/TERMS.md`
  (e.g. վարդապետ → վարդապետ, շնութիւն → շնություն,
  ցասումն → ցասում, ցանկութիւն → ցանկություն,
  բանն (reason) → բանականություն, the Ten
  Commandments as «Մի՛ սպանիր», «Մի՛ շնացիր» …).
- Numbers written with Armenian letters stay as in
  the Grabar (ՃՁԳ հազար); a slip in them is noted in
  `SOURCES.md`, not corrected.
- It is a machine translation until someone who
  reads Grabar has checked it; `SOURCES.md` says so
  for every part, and says which parts were checked.

Order: finish Ամառան հատոր (parts 2–24), then
Ձմեռան հատոր (sermons too, the same terms), then
Գիրք հարցմանց (questions and answers on theology and
philosophy: the hardest; the terms list will help).

TODO:

- [ ] `scripts/split-sentences.py`: cut a Grabar
      file into sentences as part 1 was cut (the
      rule above), with a test in `tests/` that the
      text is unchanged and every line is one
      sentence
- [ ] A test that every file in `ashkharhabar/` has
      as many lines as its partner in `grabar/`,
      blank lines in the same places
- [ ] `TERMS.md`, started from part 1
- [ ] Cut all 54 Grabar parts into sentences (one
      commit; positions saved in the reader move,
      notes follow their sentence)
- [ ] Translate Ամառան հատոր: [x] 01 [ ] 02 [ ] 03
      [ ] 04 [ ] 05 [ ] 06 [ ] 07 [ ] 08 [ ] 09
      [ ] 10 [ ] 11 [ ] 12 [ ] 13 [ ] 14 [ ] 15
      [ ] 16 [ ] 17 [ ] 18 [ ] 19 [ ] 20 [ ] 21
      [ ] 22 [ ] 23 [ ] 24
- [ ] Translate Ձմեռան հատոր: 18 parts
- [ ] Translate Գիրք հարցմանց: 12 parts
- [ ] Ask someone who reads Grabar to check a few
      parts; fix the terms list from what they find
- [ ] Later: `fetch-digilib.py` could write one
      sentence per line itself, for new books

## Plan: more Grabar authors from Digilib

After Tatevatsi, more books from Digilib
(digilib.am), fetched the same way with
`scripts/fetch-digilib.py`. The authors below were
found on 2026-11-07 in its categories Theology,
Historiography, Philosophy, Literature, Letters and
Law (modern authors left out). Not yet checked: that
each book is typed text, not only scans, and how big
it is. Historiography showed links to its first 10
pages only; there may be more.

5th century (the golden age):

- Ագաթանգեղոս (Agathangelos), History
- Կորիւն (Koriun), Life of Mashtots
- Մովսէս Խորենացի (Movses Khorenatsi), History
- Եղիշէ (Yeghishe), on Vardan and the war
- Փաւստոս Բուզանդ (Pavstos Buzand)
- Ղազար Փարպեցի (Ghazar Parpetsi)
- Եզնիկ Կողբացի (Eznik Koghbatsi), Refutation
  of the Sects
- Դաւիթ Անյաղթ (David the Invincible)
- Մամբրէ Վերծանող (Mambre Vertsanogh)
- Յովհան Մանդակունի (Hovhan Mandakuni)
- Գրիգոր Լուսաւորիչ (Gregory the Illuminator,
  the sermons under his name)

6th–10th centuries:

- Սեբէոս (Sebeos), Ղեւոնդ (Ghevond),
  Յովհան Մամիկոնեան (Hovhan Mamikonian)
- Անանիա Շիրակացի (Anania Shirakatsi)
- Կոմիտաս Աղցեցի (Komitas Aghtsetsi),
  Յովհան Օձնեցի (Hovhan Odznetsi),
  Սահակ Ձորոփորեցի, Սահակ Մռուտ
- Վրթանէս Քերթող, Մովսէս Ցուրտաւեցի
  (letters and treatises)
- Յովհաննէս Դրասխանակերտցի (Hovhannes
  Draskhanakerttsi), Ուխտանէս (Ukhtanes)
- Գրիգոր Նարեկացի (Grigor Narekatsi), Book of
  Lamentations

11th–14th centuries:

- Գրիգոր Մագիստրոս (Grigor Magistros), letters
- Ներսէս Շնորհալի (Nerses Shnorhali),
  Ներսէս Լամբրոնացի (Nerses Lambronatsi)
- Մխիթար Գոշ (Mkhitar Gosh), law code and fables
- Վարդան Այգեկցի (Vardan Aygektsi), fables
- Սամուէլ Անեցի, Մխիթար Անեցի, Կիրակոս
  Գանձակեցի, Վարդան Արեւելցի, Սմբատ Սպարապետ,
  Հեթում Պատմիչ, Ստեփաննոս Օրբելեան
  (chronicles and histories)
- Ֆրիկ (Frik), Յովհաննէս Թլկուրանցի
  (Hovhannes Tlkurantsi), poets

15th–18th centuries:

- Թովմա Մեծոփեցի (Tovma Metsopetsi)
- Առաքել Դաւրիժեցի (Arakel Davrizhetsi)
- Զաքարիա Քանաքեռցի, Զաքարիա Ագուլեցի
- Սիմէոն Լեհացի, Երեմիա Չէլէպի Քէօմիւրճեան
- Ոսկան Երեւանցի, Սիմէօն Երեւանցի,
  Աբրահամ Կրետացի, Եսայի Հասան Ջալալեան
- Many poets of the time in Literature
  (Նահապետ Քուչակ, Մարտիրոս Ղրիմեցի, Սիմէոն
  Կաֆացի, Խաչատուր Կաֆացի, …)

Not found in these categories (look elsewhere on
Digilib or in other sources): Մատթէոս Ուռհայեցի,
Թովմա Արծրունի, Յովհաննէս Երզնկացի, Կոստանդին
Երզնկացի.

Suggested order:

1. Ներսէս Շնորհալի: a churchman like Tatevatsi,
   clear language
2. Եղիշէ, Կորիւն: short classic 5th-century prose,
   the model Grabar
3. Մովսէս Խորենացի: the best-known history
4. Գրիգոր Նարեկացի: very important, very hard

TODO:

- [ ] For each author: open their books on Digilib,
      note the book ids, check the text is typed
- [ ] Fetch the first one into
      `books/grabar/<author>/`, add it to
      `books/SOURCES.md`
- [ ] Look through Historiography past page 10 and
      the other categories for authors missed here

## Plan: a contents page

The welcome on the main page lists only the
Tatevatsi works and how much of each is translated
(`FRONT` in `web/app.js`). A page of its own will
show the whole library:

- Every book in `grabar/`, grouped by author, with
  its century and kind (sermons, history, poems, …)
- For each: its parts, how many have a translation
  (`status()` in `nxgir_web.py` already counts them
  for books in parts; books in one file count too),
  and a progress bar like the one on the main page
- Each part: what it covers (from `notes/`, e.g.
  `notes/3-amaran-hator.md`), and a link to read it,
  side by side where a translation exists
- Books in another language than Grabar marked
  (Shnorhali's riddles are Middle Armenian)
- The authors still to come (the Digilib list
  above), so a visitor sees what is planned
- A link to it from the main page and the top bar

TODO:

- [ ] Choose its address (e.g. `#/contents`) and
      what it is called in Armenian
- [ ] An API answer with every book, its parts and
      their translation status (and the same file
      in `build-site.py` for the Pages copy)
- [ ] Short descriptions of the parts: a file per
      book in `notes/`, read by the page, or a
      `contents.tsv`
- [ ] The page in `app.js`, tested in
      `tests/test_web.py`

## TODO: the website

- [ ] A separate email address for the project
      (e.g. nxgir.project@gmail.com, if it is still
      free), so the author's own address
      is not on the site; then put it in `CONTACT` in
      `web/app.js` (kept in two parts there, so that
      programs gathering addresses do not find it)
- [ ] Faster Pages builds, when they get slow (more
      than about 5 minutes; now 2–3 from push to
      live). `build-site.py` builds the whole site
      each time (about 54 MB: word lookups 30 MB,
      books 21 MB), and GitHub Pages always takes the
      whole site, so only the build can be made
      faster: keep the built files between runs
      (`actions/cache`), with a hash of each book's
      text and of the build code; build again only
      the books that changed, and the word files
      only when a book's words or `grabar/` change.
      A test that a build from the cache equals a
      build from scratch

## Open questions

- Permissions: which scans and texts can be published,
  and how to work together with the Matenadaran and other
  libraries and museums
- Licenses for the texts, pictures, and code
- Where to host the scans (they take a lot of space)
- How volunteers and scholars can help: checking OCR,
  translating, describing pictures, adding knots
- Funding for hosting and scanning over the years

## Notes

(free space for ideas)
