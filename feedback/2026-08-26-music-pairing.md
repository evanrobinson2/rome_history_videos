# Trilogy music architecture

Date: 2026-08-26
Owner: `cloud-music`
Scope: music and versioning only; the story worker owns narrative structure

## Correction

The project is **three videos**, not one continuous film sharing a six-minute
suite. The earlier major → minor → major assembly was a useful compatibility
test, but it is not the score plan.

Each video may establish its own musical grammar. Continuity across the trilogy
can come from a small returning motif, voice, or instrument; it does not require
one tempo, key, or production style.

## Current score status

| Video | Story territory | Music status | Next music decision |
| --- | --- | --- | --- |
| **1** | Young Fritigern, love, wedding, union, first Hunnic wound, years of pressure | **No music yet** | Create the first film's musical identity from its own emotional rules |
| **2** | Begins with starvation and Roman treatment; humiliation, bread denied, Marcianople reversal, revolt, Adrianople | **Candidates exist** | Test the candidates against picture and narration; a cue may change grammar at the reversal |
| **3** | Fritigern fades; Alaric inherits; Rome; bread restored | **Music already exists** | Preserve it and identify the exact source master/stems in the delivery manifest |

Do not spend Film 3's score solving Films 1 or 2. Do not force Film 1 to sound
like either later film merely to make the trilogy feel branded.

## Film 1 — music brief

Film 1 needs music that can hold two truths at once:

1. ordinary life is real and worth losing;
2. danger is already present but has not yet become the governing rhythm.

### Musical behavior

- Begin from human-scale sound: breath, hand percussion, wood, skin, plucked
  strings, or a small unison hum.
- Let the wedding create actual warmth and movement. The love and union should
  not be scored as pre-tragedy from the first frame.
- The Hunnic raid should **break the established musical rule**, not merely make
  the same cue louder.
- After the raid, leave enough of the opening motif alive to show that the union
  survived.
- Across the later pressure montage, make repetition accumulate rather than
  jumping immediately to battle music.

### Avoid

- Generic epic trailer scoring.
- Cathedral choir or modern "Techno Gothic."
- A continuous ominous drone that tells the audience the wedding is doomed
  before they have lived inside it.
- Borrowing Film 2's starvation grammar before starvation begins.

### Motif opportunity

The ancestral hum can originate here as a few imperfect human voices. Later
films may transform or quote it, but they do not need to preserve Film 1's
instrumentation, tempo, or key.

## Film 2 — candidate test

Film 2 begins with starvation and Roman treatment. That means the opening music
should already understand dependence, waiting, and procedural humiliation; it
does not need to recreate Film 1's domestic opening.

The two analyzed inbox tracks remain useful candidates:

| Track | Length | Tempo | Key estimate | Measured character |
| --- | ---: | ---: | --- | --- |
| `Frozen Plain Thrace` | 3:30 | 107.7 BPM | E-flat major / G-minor ambiguity | More harmonic, darker spectral center, gradual energy rise |
| `Dust on the Steppe` | 2:44 | 112.3 BPM | E-flat minor | 2.6× denser onset activity, brighter, more percussive |

These measurements establish compatibility, not placement. The tracks share an
E-flat tonic estimate and can crossfade cleanly, but Film 2 is free to choose
one, use both, or reject both after a picture test.

### Picture-test markers

`Frozen Plain Thrace`:

- 0:00–0:16 — unusually quiet opening
- 0:16–1:47 — long stable section
- 1:47 — energy lift
- 2:23–2:59 — loudest sustained section
- 2:59–3:08 — approximately 12 dB collapse; strong aftermath or reveal space

`Dust on the Steppe`:

- 0:00–0:28 — lower-energy setup
- 0:28–1:35 — first sustained attack block
- 1:35–1:37 — two-second rupture
- 1:37–2:35 — second sustained block
- 2:35–end — low-energy exit

The decisive test is not which waveform looks better. It is which cue lets the
starvation narration remain intelligible and which musical rule-break makes
the Marcianople reversal legible.

## Film 3 — preserve the existing score

Film 3 already has music. Before editing:

1. record the exact source filename and generation/version ID;
2. preserve the highest-quality master;
3. obtain or create separate music and effects stems where possible;
4. mark the approved picture synchronization points;
5. do not replace it simply to make the trilogy sonically uniform.

Film 3 may still quote the ancestral hum or another trilogy motif if that can
be added without weakening the score Evan already chose.

## Language and alternate versions

The pipeline should treat picture, music/effects, narration, and text as
separate deliverables:

- one picture master per approved cut;
- one **M&E** master (music and effects, no narration);
- one narration stem per language;
- one subtitle/caption file per language;
- one small manifest recording language, narrator, mix, and source versions.

This makes language versions inexpensive, but not literally automatic.
Different languages expand and contract. Build breathing room into narration
holds and permit small language-specific picture retimes rather than
time-stretching speech or crushing translation.

The same structure also supports alternate musical versions:

- score-forward vs narration-forward mix;
- historically restrained vs more contemporary treatment;
- festival, classroom, social, and accessibility cuts;
- localized narration with the same M&E bed.

## Mix baseline

For any candidate picture test:

- begin around **−8 dB** below the supplied music master under narration;
- automate another **2–4 dB** of ducking on dense speech;
- keep the program true peak at or below **−1 dBTP**;
- preserve intentional low-energy holes instead of filling every pause;
- compare candidates at matched perceived loudness.

The next concrete music deliverable is a Film 1 prompt/reference brief and a
Film 2 A/B picture test. Film 3 should enter conform as an existing approved
asset, not as an open composition problem.
