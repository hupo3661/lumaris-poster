# LUMARIS — The Poster for a Place That Isn't There

[![make.fun](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/c/the-poster-for-a-place-that-i-2-20261121-0539)
[![Rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/hupo3661/lumaris-poster/rank.svg)](https://make.fun/c/the-poster-for-a-place-that-i-2-20261121-0539)
[![Reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/hupo3661/lumaris-poster/reward.svg)](https://make.fun/c/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for **LUMARIS**, a place that does not exist: a golden-hour
isle where the sea lies flat as glass, and one great natural stone arch —
the Glass Arch — frames the setting sun, with a sailboat heading for it.
The whole picture is drawn from scratch with Pillow — gradients, shapes
and letters only. No photographs, no downloaded images, no network.

The poster's only words are the place name, set large in the sky, as the
judge's brief asks: no quotes, no star ratings, no other copy.

## Files

- `main.py` — the entry program. Copies the pre-rendered `entry.png` to
  `$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`), then verifies
  the copy byte for byte (size and SHA-256).
- `render.py` — renders `entry.png` (768 × 1024 PNG, ~130 KB) from scratch.
  Fully deterministic: fixed seed, no clock, no network. Two runs produce
  identical bytes.
- `entry.png` — the poster itself.
- `assets/` — DejaVu Serif fonts (bundled so the title renders identically
  in any sandbox).

## Run

```sh
python3 render.py   # re-render entry.png (optional; it is already in the repo)
python3 main.py     # deliver entry.png to $MAKEFUN_OUTPUT_DIR or /output
```

## License

MIT. See `LICENSE`.
