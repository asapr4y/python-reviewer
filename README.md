# Python Study Room

A static, responsive Python reviewer and exam built from the two supplied PDFs. No account, database, API key, or production dependencies are required.

## Run locally

Requires Node.js. From this folder:

```sh
npm start
```

Open http://localhost:4173. The app needs HTTP to load its question bank; opening `index.html` directly is not supported. Progress, bookmarks, and the current exam are saved in this browser's local storage.

## Included

- All 76 questions: 22 in **Exam A**, 54 in **Practice set**.
- Search, source filters, bookmarks, reviewed progress, larger text, question navigation, and image enlargement.
- Exams with either/both sources, 10/25/all questions, and original or shuffled order.
- Automatic scores, correct/incorrect/unanswered counts, full answer comparison, and retrying missed questions.
- Single answers, exact multiple selection, ordered code, matching, and Yes/No selections.
- Both original PDFs, unchanged, under `public/sources/`.

Question wording and source code images are preserved. Layout whitespace is normalized, and image-based interactions use accessible select controls. The files contain conflicting or questionable answer keys: each question is graded against **its own source's marked answer**, without silently correcting it. The unnumbered item between Practice set 21 and 23 is shown as question 22. Each complete question earns 1 point; all parts must match for multipart questions. This is the site's practice scoring, not the first PDF's scaled certification score.

## Build and host

```sh
npm run build
```

Deploy the **contents of `dist/`** to any static web host. No server-side routes or environment variables are needed. `dist/` contains the entire site and source documents.

### Vercel

The repository includes `vercel.json` with these deployment settings:

| Setting | Value |
| --- | --- |
| Framework Preset | Other |
| Root Directory | Repository root (`./`) |
| Install Command | `npm ci --omit=dev` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Environment Variables | None |

Push the project to GitHub, import the repository as a new Vercel project, and deploy. Keep the Root Directory at the repository root so Vercel reads `vercel.json`. The build uses only Node.js; Python, the extraction tools, and browser test dependencies are not required for deployment. `.vercelignore` excludes local tools and test artifacts from CLI uploads.

Progress is stored per browser and site address. Progress on localhost does not transfer automatically to your Vercel address.

## Verify

```sh
npm install
npm test
npm run test:browser
```

The browser test uses an installed Google Chrome and a running `npm start` server. It exercises every question and all 200 answer selections, mixed scores, resume, results, search, progress, bookmarks, and mobile layouts.

Optional source verification requires PyMuPDF and the original PDFs at their supplied Downloads paths:

```sh
python scripts/verify_sources.py
```

The source verification independently compares all 39 multiple-choice keys to the PDF text or highlight geometry and checks byte-identical PDF copies. Multipart image keys were visually transcribed and checked. `scripts/extract_content.py` regenerates the question bank and checks source word coverage; it must be reviewed carefully if the source PDFs change.

## Main files

- `public/app.js`: application views and interactions
- `public/logic.js`: grading, shuffle, and storage helpers
- `public/questions.json`: the question bank and source-specific answers
- `public/styles.css`: desktop, mobile, large-text, and print styling
- `tests/`: scoring and browser verification

This is a personal study tool. The answer bank is delivered to the browser; it is not intended for secure or proctored exams.
