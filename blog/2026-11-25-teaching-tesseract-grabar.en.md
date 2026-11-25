# Teaching Tesseract to read Grabar

theme: tech

Grabar is classical Armenian, and standard OCR barely reads it. To type the old books faster we taught the free OCR program Tesseract to read the print of an 1859 edition. Here is how, with the numbers.

![Teaching a computer to read Grabar](ocr-grabar-1.jpg)

## The page

The test is page 101 of the 1859 edition of Smbat Sparapet's Chronicle. The type is old and decorative, so many letters look nothing like modern Armenian print. This page was never used for training.

![The scanned page, the first seven lines](ocr-grabar-2.jpg)

## Before and after

The stock Armenian model of Tesseract breaks almost every word: վասն becomes վասն?, պատճառի becomes սլատմառի, մռնչելով becomes ժոնչելով. In red are the words the program marked as uncertain or that are not found in the typed text of the book.

![The stock model's reading of the first seven lines](ocr-grabar-3.jpg)

The same lines read by our tuned model are nearly clean.

![The tuned model's reading of the same lines](ocr-grabar-4.jpg)

## The numbers

On this page the word errors fall from 51.6% to 4.9%, and the character errors from 20.7% to 1.4%. On all the held-out pages of the book (pages that were never used in training) the word errors fall from 58.7% to 9.1% and the character errors from 25.9% to 3.5%.

![Word errors, stock and tuned](ocr-grabar-5.jpg)

## How it is done

We did not train a model from nothing. We took Tesseract's Armenian model and fine-tuned it on pages of the book that were already typed by hand. The program reads each page, matches every scanned line to the typed text, and keeps only lines with less than 50% error and no unknown letters. Whole blocks of five pages (a quarter of the pages) are held out for testing, so no test page has a neighbour in training. Four thousand training steps take about five minutes on four CPUs. The result, `hye_grabar`, is 6 MB and is kept in the repository.

![The six steps of the tuning](ocr-grabar-6.jpg)

## What we learned

Every step is scored on pages the model has never seen, against the typed text. A good number can hide a bad page, so we also look at pages by eye. The word-list and LLM correction passes sometimes made the text worse, silently, so they only suggest changes for a person to check. The model trained on the 1859 book also helped on another book (Aristakes): the character errors fell from 29.9% to 14.6%, and to 12.2% when tuning started from our model.

![What we learned, and the repository](ocr-grabar-7.jpg)

## References

The book: Տարեգիրք Սմբատայ Սպարապետի (Smbat Sparapet's Chronicle), Paris, 1859, edited by K. Shahnazareants. The Google scan was put on the Internet Archive by Robert Bedrosian: https://archive.org/details/SmbatGrabarTaregirk1859. A copy is in the repository, in sources/shahnazareants-1859/.

Tesseract OCR, the program: https://github.com/tesseract-ocr/tesseract. Its documentation and training guide: https://tesseract-ocr.github.io/tessdoc/.

The base model we started from: the float `hye` model of tessdata_best, https://github.com/tesseract-ocr/tessdata_best. (The `hye` that comes with the system is integer-only and cannot be tuned.)

Our code, scores and notes: ocr/README.md in https://github.com/serjhnn/nx-gir. The tuned model is ocr/models/hye_grabar.traineddata.
