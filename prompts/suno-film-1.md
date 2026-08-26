# Suno prompts — Film 1 (Young Fritigern)

Use Custom mode. **Instrumental** for all of these unless noted.
Paste the Style block into Style. Leave Lyrics empty, or put `[Instrumental]` only.

Avoid: techno gothic, epic trailer choir, cathedral reverb, modern trap drums.

---

## A — Homeland / ordinary life (open the film)

**Title suggestion:** `Wood Smoke North`

**Style:**
```
Instrumental folk ambient, 88 BPM, D major. Intimate and human-scale.
Soft frame drum and skin hand percussion, sparse plucked gut-string or
lyre ostinato, distant wood flute, warm room tone. A few imperfect human
voices humming a simple unison motif — not a choir, not polished. Quiet
opening, pastoral, lived-in. No epic drums, no synth bass, no trailer
brass, no techno. Clean headroom for spoken narration.
```

**Custom / Lyrics field:**
```
[Instrumental]
[Intro: quiet breath, soft frame drum alone]
[Verse feel: plucked ostinato + low hum]
[Bridge: flute answers the hum]
[Outro: hum alone, fading]
```

---

## B — Wedding / union (warmth that is real)

**Title suggestion:** `Two Peoples One Fire`

**Style:**
```
Instrumental ceremonial folk dance, 96 BPM, G major. Joyful but grounded,
not triumphant. Hand claps, frame drums, ankle bells, plucked strings,
small reed pipe. Group of human voices humming in loose unison — village
wedding, imperfect and alive. Warm midrange, intimate mix, outdoor fire
feel. No orchestral swell, no EDM drop, no dark choir. Leave space under
the midrange for spoken word.
```

**Custom / Lyrics field:**
```
[Instrumental]
[Build: claps enter, soft dance pulse]
[Chorus feel: humming motif returns fuller]
[Break: drums thin, two voices only]
[Return: dance with restraint]
[End: one held hum]
```

---

## C — Raid break (break the musical rule)

**Title suggestion:** `Ridge Shadow Break`

Generate as a **separate short cue**, then edit against A/B — do not ask Suno
to do the whole film in one take.

**Style:**
```
Instrumental sudden disruption, 110 BPM, D minor. Abrupt entrance after
silence. Harsh struck wood, distant horse-rhythm percussion, dry bow scrapes,
low drones that cut rather than bloom. The earlier humming motif appears
broken and incomplete. Short, tense, not epic battle music. No techno,
no big cinematic brass, no choir. Aggressive but brief — under 90 seconds
preferred.
```

**Custom / Lyrics field:**
```
[Instrumental]
[Hard cut in]
[Sparse horse-rhythm percussion]
[Broken hum fragment]
[Sudden stop]
```

---

## D — After the raid / years of pressure (motif survives)

**Title suggestion:** `Wanderers Together`

**Style:**
```
Instrumental road hymn, 92 BPM, A minor leaning toward modal. Sparse.
Walking pulse on low drum, thin plucked ostinato, wind-like flute in
long tones. The humming motif returns quieter, fewer voices, same shape.
Endurance not despair. Cold air, open landscape, no battle drums, no
horror score, no synth pads that wash out speech. Dynamic but restrained;
leave ducking room for narration.
```

**Custom / Lyrics field:**
```
[Instrumental]
[Walking pulse]
[Quiet hum returns]
[Sparse flute]
[Long fade on motif]
```

---

## E — Full Film 1 lyric pass (spoken word over bed)

Use this when you want **one song** that carries Video 1: homeland → love → wedding
→ raid → Alaric born → years of pressure → the decision to walk.

Spoken, rhythmic, short clauses. Male voice preferred. Not sung. Not theatrical
patter. Not a choir.

**Title suggestion:** `They Became One People`

**Style:**
```
Spoken word over mid-tempo folk groove, 92 BPM, modal D. Dry male spoken
voice upfront, clear consonants, on-grid, conversational memory — not singing,
not autotune, no backing vocals. Bed: soft frame drum, sparse plucked
ostinato, low wood flute, imperfect human humming motif underneath the
speech. Intimate room mix. Quiet pastoral opening, warmer for the wedding,
harder and thinner after the raid, walking pulse at the end. No techno,
no epic trailer choir, no cathedral reverb, no trap 808s. Leave headroom
for the voice.
```

**Lyrics (paste into Custom):**
```
[Verse 1]
We had the north.
Wood smoke. Wet grass.
A wheel that still turned.

I was not a king.
I was a man who wanted land,
a wife,
a fire that stayed lit.

Two peoples lived apart —
my side the wanderers,
her side the horsemen of the steppe.
Proud. Separate. Alive.

Then I loved her.
Not for alliance.
For her.

[Chorus]
Love made us one people
before the world asked us to be.

[Verse 2]
We married under open sky.
Two camps became one fire.
Elders watched.
Children danced.
Bread passed hand to hand.

For one night the arguments were over.
For one night the north felt finished and whole.

[Bridge — raid]
Then the ridge learned a new shape.
Horse. Rider. Horse. Rider.
Not a battle yet —
a shadow learning how to ride.

They came for the wedding.
In the chaos each side pulled its own toward safety.
We saved the bride.
We saved the groom.
The old ones did not come back.

Love united us.
Violence took the generation that kept us apart.
We were the bridge that remained.

[Verse 3]
I did not ask to lead.
Responsibility fell on me anyway.

We became wanderers together.
Her people and mine —
one road, one hunger, one name for home
that we could no longer point to on a map.

A son was born from that union.
Alaric.
Child of wanderers.
Child of horsemen.
Heir to the love and the wound.

He learned the wagon before he learned the world.
He watched adults argue the weather.
He did not know yet what bread would cost.

[Verse 4]
Years turned.
The raids that touched the wedding
became a wall moving west.
We did not leave the first time.
We left when staying meant death.

So we walked.
Not for glory.
For food. For land. For the right to keep a child alive.

Rome was a promise on the far side of a river.
We carried what we could.
We left what we could not.

[Outro]
This is how a people is made —
not in a throne room,
but in a wedding that burns,
in a child who watches,
in a road that will not end.

We had the north.
Then we had each other.
Then we had only the walk.
```

**Notes for generation:**
- If Suno sings too much, add to Style: `strictly spoken word, zero melody in the vocal`.
- If the bed gets too big after the raid, regenerate Bridge alone with prompt C's style
  and splice.
- Do **not** land “they will not beg again” here — that line belongs to Film 2/3 after
  Rome’s humiliation.

---

## How to use while images arrive

1. Generate **A** and **B** first — those set the mood against homeland and wedding frames.
2. Generate **C** as a short hard cut for the raid redo.
3. Generate **D** for the pressure montage into Film 2.
4. Generate **E** when you want a full spoken-word Film 1 pass to sit under picture.
5. Keep the humming motif recognizable across takes; if Suno drifts, regenerate with
   `same simple humming motif as before` added to Style.
6. Drop winners into `feedback/inbox/` with names like
   `2026-08-26-wood-smoke-north.mp3` so cloud can measure them.
