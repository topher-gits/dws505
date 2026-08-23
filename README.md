# 505 Armory Draw

Weekly allocation of 8 armories across 5 alliances, drawn at random but
identically for everyone who opens the link.

**Live at <https://dws505.com/armory>** — that is the link to share with all
five alliances; everyone who opens it sees the same draw. A specific week has
its own link, e.g. <https://dws505.com/armory#2026-W34>.

`armory.html` is the whole page: one self-contained file, no build step, no
dependencies, no backend.

## How the draw works

The result is a pure function of the ISO week and the alliance roster:

```
seed     = "armory-draw|v1|" + weekKey + "|" + alliances.join(",")
hash     = SHA-256(seed)
rng      = mulberry32(first 32 bits of hash)
order    = Fisher–Yates shuffle of the 8 armories using rng
slots    = [rank1, rank1, rank2, rank2, rank3, rank3, rank4, rank5]
```

The n-th armory in the shuffled order goes to the n-th slot. Nothing is
stored and nothing is random at page load — every visitor computes the same
answer from the same two inputs.

`weekKey` is the ISO-8601 week in **UTC**, so the draw rolls over at
**Monday 00:00 UTC** and stays fixed for the rest of the week. Past and
future weeks are browsable with the arrows; the sealed-vault animation only
plays for the current week.

## Reproducing a draw

Nothing is stored, so any week can be recomputed from the source. The seed
string is `armory-draw|v1|<weekKey>|<alliance tags, comma separated>`:

```bash
printf '%s' "armory-draw|v1|2026-W34|AoR,Boo,NYP,UF,PARs" | shasum -a 256
```

The first 32 bits of that hash seed `mulberry32`, which drives a Fisher–Yates
shuffle of the 8 armories. Both are short, readable functions in `armory.html`
if anyone ever wants to check a week by hand.

## Updating the roster

Edit the `CONFIG` block at the top of `armory.html` and redeploy:

```js
const CONFIG = {
  title:      "505 Armory Draw",
  version:    "v1",
  alliances:  ["AoR", "Boo", "NYP", "UF", "PARs"],  // rank order 1..5
  allocation: [2, 2, 2, 1, 1],
  armories:   ["01","02","03","04","05","06","07","08"]
};
```

Two things to know:

- **The roster is part of the seed.** Changing the rank order changes every
  week's result, past and future — not just the current one. That is by
  design (the draw is a function of its inputs), but it means the git history
  of this file is the record of what the inputs were when.
- **`allocation` must sum to the number of armories**, and must be the same
  length as `alliances`. If it isn't, the page refuses to draw and shows a
  configuration error instead of a silently wrong result.

`title` is display-only — it is not part of the seed, so renaming the page
never changes a draw. Bump `version` if you ever want to deliberately re-roll every week from
scratch.

## Local preview

```bash
python3 -m http.server 8137
```

Then open <http://localhost:8137/armory.html>. Serving over HTTP rather than
opening the file directly keeps `localStorage` working.

## Deploying to dws505.com/armory

Drop `armory.html` at the site root. Cloudflare Pages, Netlify and Vercel all
serve extensionless URLs by default, so `dws505.com/armory` resolves to it
with no redirect rules or config needed.

Two things worth knowing:

- **Nothing in the page depends on its filename.** Week-sharing links are
  built from `location.pathname`, so they come out as
  `dws505.com/armory#2026-W34` rather than with the extension baked in.
- **Don't add a long `Cache-Control` for this file.** All three hosts default
  HTML to `must-revalidate`, which is what you want: when you edit the roster
  and redeploy, viewers pick it up on their next visit. A hard cache would
  leave them looking at the previous week's rank order and therefore the
  wrong assignment.
