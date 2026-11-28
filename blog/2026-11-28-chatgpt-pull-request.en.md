# Send a translation from your phone with ChatGPT

theme: tech

You do not need a computer, git or any command to help with the translations. If you have ChatGPT on your phone, it can open a pull request for you: a proposal to add your file to the nxGir repository. The owner reads it and, if it is good, adds it to the site. This is how to set it up, and a first test that changes nothing but one line.

## 1. Install GitHub and sign in

The pull request lives on GitHub, so you need an account there. On your phone, install the GitHub app (Google Play or the App Store, by GitHub, Inc.) and open it. Tap Sign in, or create a free account if you have none, and sign in. You will use the app later to open and read your pull request. You can also do all this in the browser, at github.com.

## 2. Add the GitHub plugin

Open the menu of ChatGPT and tap Customize.

![The ChatGPT menu, with Customize marked](chatgpt-pr-1.webp)

Tap Plugins.

![The Customize page, with Plugins marked](chatgpt-pr-2.webp)

Search for "github" and tap the plus beside the GitHub plugin by OpenAI. Sign in to GitHub when it asks, and allow it to use your repositories.

![Searching for github in the plugins, the plus marked](chatgpt-pr-3.webp)

## 3. Ask for a test pull request

Start a new chat and write:

```
please make a test pull request with my name to the serjhnn/nx-gir project
```

Use the name you want to be credited with: it is shown above the parts you work on.

## 4. Press Allow

ChatGPT asks before it does anything on GitHub. Here it wants to make a new branch, a separate copy of the files where your change waits, so nothing touches the main branch. Read what it asks and press Allow once (or Always allow, if you trust it for every such step).

![ChatGPT asks to create a branch in serjhnn/nx-gir](chatgpt-pr-4.webp)

## 5. The result

After a moment you get a card: the number of the pull request, the repository, the branch it comes from, the files changed and a button, Open pull request, that shows it on GitHub. In a test it changes only one file by two lines, and nothing is merged into the main branch.

![The pull request is created](chatgpt-pr-5.webp)

## Now with a real translation

When the test works, you can go on the same way with a real translation.

Tell ChatGPT which part of which book you want to translate, and ask it to follow the guide in the repository, "TRANSLATION_GUIDE.md". The main rules: write the modern Armenian for each Grabar line on one line, and leave the chapter headings and lines as they are.

Ask ChatGPT to:

- Put the translated file next to the other translations, in the "books/ashkharhabar/" folder.
- Add a new line to "books/TRANSLATIONS.tsv" with the status "machine".
- Create a pull request.

Your translation appears on the site only after the author of the site has approved the pull request.

Translations are published under the CC BY-SA 4.0 license (details in "CONTRIBUTING.md"). By sending a translation you agree to the terms of this license.
