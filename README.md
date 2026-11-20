# The world in one day — Friday 20 November 2026

A 1024×1024 cream-paper news front page: **40 stories from 7 regions**, with 13 original illustrated cards, 27 numbered briefs, six statistics, a dotted locator map, source and status labels, and a Thursday date check. Story copy and attribution follow the supplied competition brief; selected briefs omit trailing clauses to fit the page.

`python3 gen.py` deterministically renders `entry.png` with Pillow and system fonts, checks every text block and illustration inset, and prints section measurements and the image hash. All 13 card decks retain their supplied wording. The dense format uses up to five secondary deck lines and 9.5px brief text; all type is at least 9.5px. `layout.json` records the measured layout.

`main.ts` uses only Node standard-library APIs: it resolves the PNG relative to itself, validates the signature, IHDR, 1024×1024 dimensions and 1 MiB limit, then copies it to `MAKEFUN_OUTPUT_DIR` (default `/output`). Run with a Node version that supports direct `.ts` execution, such as current Node 22 releases.

`python3 verify.py` checks two identical renders, two identical copies from different working directories, image dimensions and size, layout budgets, and seven invalid-PNG rejection cases. Verification artifacts stay inside this repository and are removed after the check. The available verification runtime is Node 24.22.1.

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Brengsek27/news-image-20261120-r1/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Brengsek27/news-image-20261120-r1/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
