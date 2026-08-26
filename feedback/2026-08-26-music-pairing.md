# Music pairing — Fritigern to Alaric

Date: 2026-08-26  
Scope: music lane only; this does not revise the story arc  
Sources:

- `feedback/inbox/2026-08-25-frozen-plain-thrace.mp3`
- `feedback/inbox/2026-08-24-dust-on-the-steppe.mp3`
- `mind/handoffs/2026-08-25-fritigern-alaric-story-arc-to-cloud-production.md`

## Decision

Use the tracks as one **major → minor → major** suite, not as competing
candidates.

- **Frozen Plain Thrace** is the human-world cue: home, migration, dependence,
  and the final restoration of bread.
- **Dust on the Steppe** is the operation-and-war cue: the banquet reversal,
  Marcianople, revolt, and Adrianople.
- Return to a short **Frozen Plain Thrace** reprise after the war cue. The
  ending should resolve to self-possession, not remain in battle mode.

The musical hinge is unusually clean: both tracks center on E-flat, with
`Frozen Plain Thrace` estimated in E-flat major and `Dust on the Steppe` in
E-flat minor. The tonic stays fixed while the moral weather changes.

## Why this pairing works

These are measured properties, not listening impressions:

| Property | Frozen Plain Thrace | Dust on the Steppe | Editorial use |
| --- | ---: | ---: | --- |
| Length | 3:30 | 2:44 | A two-cue film can run about 6:14 before narration holds |
| Tempo | 107.7 BPM | 112.3 BPM | War accelerates by only 4.6 BPM; it feels related, not like a new film |
| Key estimate | E-flat major | E-flat minor | Same tonic makes the mode pivot the emotional turn |
| Onset rate | 1.62/sec | 4.24/sec | Dust supplies 2.6× denser attack activity |
| Harmonic/percussive ratio | +16.1 dB | +9.7 dB | Frozen leaves more room for reflective narration; Dust is the attack cue |
| Median spectral centroid | 409 Hz | 1068 Hz | Dust is materially brighter and more cutting |
| Integrated RMS | −13.36 dBFS | −14.17 dBFS | Similar overall level; transitions will not require a large gain jump |
| True sample peak in current decode | −0.61 dBFS | −0.48 dBFS | Neither decoded file clips; both still need narration ducking |

Key estimates come from chroma correlation and should be treated as estimates,
especially because `Frozen Plain Thrace` also correlates strongly with G minor.
Tempo estimates were independently cross-checked against median beat intervals.

## First-pass cue sheet

This is an edit map for the current father-to-son continuity. The story-arc
worker can move the picture beats without changing the musical logic.

### Cue A — `Frozen Plain Thrace`

| Music time | Story function | Cut logic |
| --- | --- | --- |
| 0:00–0:16 | Part I: ordinary life; bread freely shared; first human humming | Preserve the unusually quiet opening; do not begin with explanatory narration at full density |
| 0:16–1:47 | Part II: pressure, departure, wagons, the walk | Long stable section supports geographic and domestic montage |
| 1:47–2:14 | The crossing becomes Roman procedure | First major energy lift; tighten visual cuts without changing cue |
| 2:14–2:59 | Part III: disarmament, hunger, kneeling, boot + tied hand | Highest sustained energy in this cue; land child Alaric's witness here |
| 2:59–3:08 | Break / held image | The measured level falls by roughly 12 dB; use this as the breath before the reversal |

At 2:59, either hold on Alaric or let the ancestral hum survive alone. Do not
fill the drop with more score.

### Cue B — `Dust on the Steppe`

Crossfade from E-flat major to E-flat minor over the quiet break. Do not
hard-cut merely because the BPM changes.

| Music time | Story function | Cut logic |
| --- | --- | --- |
| 0:00–0:28 | Part IV: banquet setup; apparent vulnerability; training flashes begin | Lower-energy opening lets the audience read the plan before the attack |
| 0:28–1:35 | Reversal: the Goths were prepared; Marcianople erupts | The track's largest early level jump is the reveal/attack point |
| 1:35–1:37 | Two-second rupture | Use for wound, blackout, date card, or temporal break—not another action cut |
| 1:37–2:35 | Part V: revolt; wagon fighting; Adrianople; Valens trapped | Second sustained block carries the military consequence |
| 2:35–2:44 | Part VI: aftermath; Fritigern begins to fade | Natural low-energy exit; remove triumph from the victory |

### Cue C — `Frozen Plain Thrace` reprise

The existing 3:08–3:30 tail is only 22 seconds, so it is enough for a proof
edit but not for the full Alaric/Rome/bread ending. For the final cut, make a
60–90 second instrumental extension in the same E-flat-major world:

1. adult Alaric inherits the memory;
2. Rome is reached without victory music;
3. the cue strips back to household scale;
4. a parent gives bread to a child;
5. end on “They will not beg again.”

Bring back the human humming motif here. The voices should now sound communal,
but still human and intimate—not a cathedral choir.

## Narration mix

Both files are finished music masters, not dialogue beds. Use automation
rather than one static trim:

- Start at **−8 dB** relative to the supplied masters under narration.
- Duck another **2–4 dB** on dense spoken passages.
- Let the 0:28 Dust attack rise only after the reversal line clears.
- Keep the 2:59 Frozen break and 2:35 Dust exit substantially unfilled.
- Target dialogue around **−16 LUFS short-term** and keep the final program
  true peak at or below **−1 dBTP**.
- If spoken-word delivery is locked to the beat, do not time-stretch one cue
  to the other. The 4.6 BPM acceleration is part of the design.

## What is still missing

The two existing tracks cover Parts I–VI well but do not give Part VII and the
bread-restored coda enough room. The next music deliverable should be the
E-flat-major reprise/extension, not a third unrelated battle cue.

This preserves the current split of work: story structure can change, while
the score remains organized around one tonic and three states—human world,
organized violence, human world restored.
