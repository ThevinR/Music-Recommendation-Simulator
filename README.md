# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify or YouTube mostly learn from behavior rather than from any stated description of taste. They watch what millions of people play, skip, save, and repeat, then infer that if you resemble other listeners, you will probably like what they liked — a pattern called collaborative filtering. On top of that they layer audio analysis, listening context like time of day, and a constant stream of feedback that retrains the model, which means the system's idea of "good" is learned statistically and is rarely something a person could read and check. My version deliberately gives all of that up. It has no user history, no other listeners to compare against, and nothing that learns; it only compares a song's stored attributes against preferences the user states outright. What it prioritizes instead is transparency and predictability: every recommendation comes from a weighted score over four features — genre match, mood match, closeness to a target energy level, and an acoustic bonus — so any ranking can be traced back to the exact rules that produced it, and every result arrives with a plain-language reason attached. The tradeoff is that it cannot discover anything surprising and cannot improve on its own, but it is small enough to be fully explained, which is the point of the exercise.

### The data

Each `Song` carries ten attributes loaded from `data/songs.csv`: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`. Of those, the scorer only reads four — `genre`, `mood`, `energy`, and `acousticness`. The rest are present in the data so that later experiments (adding tempo or valence to the score) can use them without changing the loader.

A `UserProfile` stores four stated preferences: `favorite_genre`, `favorite_mood`, `target_energy` (a float on the same 0–1 scale as a song's energy), and `likes_acoustic` (a boolean). Nothing is inferred or remembered — the profile is exactly what the user says about themselves.

### Algorithm Recipe

Every song in the catalog is scored independently against the profile. Points are additive, and each point award also appends a human-readable reason, so the explanation is built from the same branches that produce the number.

| Signal | Points | Example reason |
|---|---|---|
| Genre match | **+2.0** | "matches your favorite genre (pop)" |
| Mood match | **+1.5** | "fits the mood you're after (chill)" |
| Energy closeness | **+1.5 × (1 − \|song.energy − target_energy\|)** | "energy 0.62 is close to your target 0.65" |
| Acoustic bonus (only if `likes_acoustic` and `acousticness ≥ 0.6`) | **+0.5** | "acoustic, which you tend to like" |

The maximum possible score is 5.5. Both energy values are on a 0–1 scale, so the distance term already falls in [0, 1]; it is clamped at 0 defensively.

**Why these weights.** Genre carries the most weight because it is the coarsest filter — a metal track will not satisfy a lo-fi listener no matter how well the energy lines up, so getting genre wrong is the most visible failure. Mood sits at 1.5 rather than the more common 1.0 because mood is the language people actually use when asking for music ("something chill"); at 1.0, a single near-perfect energy score could outrank an exact mood match, which felt wrong. Energy is continuous and capped at 1.5 so that it acts as a tiebreaker *within* a genre/mood group rather than as a driver across groups. The acoustic bonus is a small nudge because it is a stated like with no matching dislike — penalizing non-acoustic tracks would over-constrain an already tiny catalog.

The resulting ordering is defensible at a glance: a song matching both genre and mood starts at 3.5 and can never be beaten by a song matching only one of them.

### Data flow

```
INPUT                PROCESS                       OUTPUT
user prefs  ─┐
             ├─► for each song in catalog ─► sort by score DESC
songs.csv ──┘       score_song(prefs, song)     tiebreak on title
  (load_songs)      → (score, reasons)          take top K
                                                join reasons → explanation
                                             → [(song, score, explanation)]
```

The loop scores *every* song, including poor matches — no filtering happens inside it. Cutting down to the top K happens once, after sorting, which keeps K relevant in exactly one place and makes the system easy to debug by printing the full ranked list. Ties are broken alphabetically by title so that repeated runs produce identical output.

### Expected biases

Because the weights are hand-chosen rather than learned, their blind spots are predictable, which is the main advantage of a system this small:

- **Genre is over-prioritized.** At +2.0, genre outweighs mood, and a song that nails the user's mood and energy but sits in an adjacent genre can be ranked below a genre match that fits the mood poorly. A listener who wants "something chill" may get an upbeat track from their favorite genre instead.
- **Popular genres in the catalog crowd out the rest.** Scoring is per-song with no diversity constraint, so if the CSV happens to contain many pop songs, a pop fan's top 5 will likely be all pop. The system cannot surface a strong cross-genre match.
- **Exact string matching is brittle.** Genre and mood are compared with equality, so "lofi" and "lo-fi", or "happy" and "upbeat", score as total mismatches despite being near-synonyms. This silently penalizes whichever labels the catalog happens not to use.
- **Stated taste is not real taste.** The profile captures what a user claims to like, which research on recommenders consistently shows diverges from what people actually play. There is no feedback loop to correct that gap.
- **No novelty, by construction.** The system can only rank what best matches a stated profile, so it will never recommend something surprising. It reinforces the user's existing preferences every single run — a filter bubble, but an honest and inspectable one.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Running `python src/main.py` scores all four built-in taste profiles against the 18-song catalog in `data/songs.csv` and prints the top 5 for each. The terminal output is reproduced verbatim below.

> **Note:** this section is the **baseline** run, captured with the original weights (genre 2.0, energy 1.5, max 5.50). `recommender.py` currently carries the weight-shift experiment described under [Experiments You Tried](#experiments-you-tried), so a fresh run will print scores out of 6.00. Revert the two constants to reproduce the output below.

### Profile 1 — High-Energy Pop

```
================================================================
                    PROFILE: High-Energy Pop                    
================================================================
  Favorite genre : pop
  Favorite mood  : happy
  Target energy  : 0.85
  Likes acoustic : no

================================================================
                     TOP 5 RECOMMENDATIONS                      
================================================================

  1. Sunrise City
     Neon Echo  |  pop / happy
     Score: 4.96 / 5.50
     Why:
       - genre match: pop (+2.0)
       - mood match: happy (+1.5)
       - energy 0.82 vs target 0.85 (+1.46)

  2. Gym Hero
     Max Pulse  |  pop / intense
     Score: 3.38 / 5.50
     Why:
       - genre match: pop (+2.0)
       - energy 0.93 vs target 0.85 (+1.38)

  3. Rooftop Lights
     Indigo Parade  |  indie pop / happy
     Score: 2.87 / 5.50
     Why:
       - mood match: happy (+1.5)
       - energy 0.76 vs target 0.85 (+1.36)

  4. Ultraviolet Hours
     Pastel Machine  |  house / euphoric
     Score: 1.46 / 5.50
     Why:
       - energy 0.88 vs target 0.85 (+1.46)

  5. Storm Runner
     Voltline  |  rock / intense
     Score: 1.41 / 5.50
     Why:
       - energy 0.91 vs target 0.85 (+1.41)

================================================================
```

**Reading the results.** The top pick scores 4.96 of a possible 5.50 by hitting genre, mood, and energy at once. The more interesting result is the gap between #2 and #3: "Gym Hero" matches the genre but has an `intense` mood, while "Rooftop Lights" is `happy` but filed under `indie pop`. The genre weight of 2.0 pushes the mood mismatch above the near-miss genre match — a concrete instance of the genre over-prioritization and exact-string-matching biases described above. A listener asking for upbeat pop would arguably prefer #3. Note also that #4 and #5 match nothing but energy, yet still appear as "recommendations"; with only 18 songs the list runs out of genuine matches after three.

### Profile 2 — Chill Lofi

```
================================================================
                      PROFILE: Chill Lofi                       
================================================================
  Favorite genre : lofi
  Favorite mood  : chill
  Target energy  : 0.35
  Likes acoustic : yes

================================================================
                     TOP 5 RECOMMENDATIONS                      
================================================================

  1. Library Rain
     Paper Lanterns  |  lofi / chill
     Score: 5.50 / 5.50
     Why:
       - genre match: lofi (+2.0)
       - mood match: chill (+1.5)
       - energy 0.35 vs target 0.35 (+1.50)
       - acoustic pick (+0.5)

  2. Midnight Coding
     LoRoom  |  lofi / chill
     Score: 5.39 / 5.50
     Why:
       - genre match: lofi (+2.0)
       - mood match: chill (+1.5)
       - energy 0.42 vs target 0.35 (+1.40)
       - acoustic pick (+0.5)

  3. Focus Flow
     LoRoom  |  lofi / focused
     Score: 3.92 / 5.50
     Why:
       - genre match: lofi (+2.0)
       - energy 0.40 vs target 0.35 (+1.42)
       - acoustic pick (+0.5)

  4. Spacewalk Thoughts
     Orbit Bloom  |  ambient / chill
     Score: 3.40 / 5.50
     Why:
       - mood match: chill (+1.5)
       - energy 0.28 vs target 0.35 (+1.40)
       - acoustic pick (+0.5)

  5. Coffee Shop Stories
     Slow Stereo  |  jazz / relaxed
     Score: 1.97 / 5.50
     Why:
       - energy 0.37 vs target 0.35 (+1.47)
       - acoustic pick (+0.5)

================================================================
```

**Reading the results.** This is the only profile that reaches a perfect 5.50 — "Library Rain" hits all four signals with an exact energy match. It is also the profile the catalog serves best, because lo-fi is the one genre with multiple entries. The #3/#4 pair shows the weighting working as designed in the other direction from Profile 1: a `lofi` track with the wrong mood (3.92) edges out an `ambient` track with the right mood (3.40), which is the intended behavior when genre is the coarser filter. Two of the LoRoom tracks appear in the same list, hinting at the artist-concentration risk noted under Limitations — nothing in the scorer penalizes recommending the same artist twice.

### Profile 3 — Deep Intense Rock

```
================================================================
                   PROFILE: Deep Intense Rock                   
================================================================
  Favorite genre : rock
  Favorite mood  : intense
  Target energy  : 0.90
  Likes acoustic : no

================================================================
                     TOP 5 RECOMMENDATIONS                      
================================================================

  1. Storm Runner
     Voltline  |  rock / intense
     Score: 4.98 / 5.50
     Why:
       - genre match: rock (+2.0)
       - mood match: intense (+1.5)
       - energy 0.91 vs target 0.90 (+1.48)

  2. Gym Hero
     Max Pulse  |  pop / intense
     Score: 2.96 / 5.50
     Why:
       - mood match: intense (+1.5)
       - energy 0.93 vs target 0.90 (+1.46)

  3. Ultraviolet Hours
     Pastel Machine  |  house / euphoric
     Score: 1.47 / 5.50
     Why:
       - energy 0.88 vs target 0.90 (+1.47)

  4. Iron Verdict
     Ashfall Rite  |  metal / angry
     Score: 1.40 / 5.50
     Why:
       - energy 0.97 vs target 0.90 (+1.40)

  5. Sunrise City
     Neon Echo  |  pop / happy
     Score: 1.38 / 5.50
     Why:
       - energy 0.82 vs target 0.90 (+1.38)

================================================================
```

**Reading the results.** The most revealing output of the four. Only one rock song exists in the catalog, so after #1 the ranking has no genre signal left and collapses to energy alone — scores drop from 4.98 to 2.96 to 1.47 within three slots. The consequence is visible at #3 and #4: a `house / euphoric` track outranks `Iron Verdict` (metal / angry) for a listener who asked for intense rock, purely because 0.88 sits marginally closer to 0.90 than 0.97 does. Genre adjacency is invisible to the scorer — metal is no nearer to rock than house is — and the ceiling of 1.5 energy points means the bottom of every sparse list is decided by hundredths of a point. A "Top 5" framing here overstates how much the system actually found; #3 onward are filler, and the explanations honestly say so by listing a single energy line.

### Profile 4 — Acoustic Wind-Down

```
================================================================
                  PROFILE: Acoustic Wind-Down                   
================================================================
  Favorite genre : folk
  Favorite mood  : nostalgic
  Target energy  : 0.30
  Likes acoustic : yes

================================================================
                     TOP 5 RECOMMENDATIONS                      
================================================================

  1. Grandfather's Porch
     Rye Hollow  |  folk / nostalgic
     Score: 5.38 / 5.50
     Why:
       - genre match: folk (+2.0)
       - mood match: nostalgic (+1.5)
       - energy 0.38 vs target 0.30 (+1.38)
       - acoustic pick (+0.5)

  2. Spacewalk Thoughts
     Orbit Bloom  |  ambient / chill
     Score: 1.97 / 5.50
     Why:
       - energy 0.28 vs target 0.30 (+1.47)
       - acoustic pick (+0.5)

  3. Sea Glass Waltz
     Luiza Prado  |  bossa nova / dreamy
     Score: 1.96 / 5.50
     Why:
       - energy 0.33 vs target 0.30 (+1.46)
       - acoustic pick (+0.5)

  4. Library Rain
     Paper Lanterns  |  lofi / chill
     Score: 1.92 / 5.50
     Why:
       - energy 0.35 vs target 0.30 (+1.42)
       - acoustic pick (+0.5)

  5. Coffee Shop Stories
     Slow Stereo  |  jazz / relaxed
     Score: 1.90 / 5.50
     Why:
       - energy 0.37 vs target 0.30 (+1.40)
       - acoustic pick (+0.5)

================================================================
```

**Reading the results.** The sparsest result of the four: one folk song, then a four-way near-tie spanning 1.97 to 1.90 — a spread of 0.07 points across four completely different genres. Every one of #2–#5 earns exactly the same two reasons (low energy, acoustic), so the ordering among them is effectively arbitrary from the listener's point of view even though it is fully deterministic. This is the clearest demonstration that the acoustic bonus is too small to differentiate: it is awarded to all four, so it shifts every score equally and breaks no ties. Worth noting the system never signals low confidence — a 1.90 "recommendation" is presented in the same format as the 5.50 one in Profile 2.

### Across all four profiles

Each profile's #1 pick is the song a human would have chosen, which is the system working as intended: when an exact genre + mood match exists in the catalog, the weighting finds it every time. The failures all live further down the list. The quality of a recommendation list is bounded by how many songs in the catalog share the requested genre — lo-fi has three and produces a credible top 4, while rock and folk have one each and degrade into energy-sorted filler by slot 2 or 3. The scorer has no concept of "no good match remaining," so it always returns exactly K rows with the same confident formatting regardless of whether the 5th row scored 1.90 or 4.50. A useful next change would be a minimum score threshold, or printing a "weak match" marker below some cutoff, so the output distinguishes what it found from what it merely ranked.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment 1 — Weight shift: energy doubled, genre halved

**The change.** In `score_song`, `GENRE_POINTS` went from 2.0 to 1.0 and `ENERGY_POINTS` from 1.5 to 3.0. Mood (1.5) and the acoustic bonus (0.5) were left alone. This inverts the original priority order: energy becomes the dominant signal and genre drops to the weakest of the three main terms.

**Checking the math stayed valid.** Energy closeness is `max(0, 1 - |song.energy - target|)`, which stays in [0, 1] regardless of the multiplier, so the energy term spans [0, 3.0] and no term can go negative. The maximum possible score moves from 5.50 to 6.00. Rather than re-typing that number, the weights are now module-level constants and `MAX_SCORE` is derived from them, with `main.py` importing it instead of hardcoding `/ 5.50` — the old display would have under-reported the denominator after this change. Sweeping both a best-case and a degenerate profile across the full catalog confirmed observed scores land in exactly [0.00, 6.00].

**What happened.** Two of the four profiles reordered; two did not.

| Profile | Before (5.50 scale) | After (6.00 scale) | Changed? |
|---|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, **Rooftop Lights, Gym Hero** | #2/#3 swap |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts | Library Rain, Midnight Coding, **Spacewalk Thoughts, Focus Flow** | #3/#4 swap |
| Deep Intense Rock | Storm Runner, Gym Hero, Ultraviolet Hours, Iron Verdict | identical | no |
| Acoustic Wind-Down | Grandfather's Porch, Spacewalk Thoughts, Sea Glass Waltz, Library Rain | identical | no |

**More accurate, or just different?** Mostly just different — with one genuine improvement.

The improvement is the High-Energy Pop swap. Under the original weights, `Gym Hero` (pop / **intense**) outranked `Rooftop Lights` (**indie pop** / happy) purely because exact genre equality was worth more than a mood match. That was flagged above as the clearest misranking in the whole system: a listener asking for upbeat pop wants the happy indie-pop track, not the aggressive gym track. Halving genre fixed it for the right reason — the fix comes from genre no longer overpowering mood, not from a coincidence of energy values.

The Chill Lofi swap is a wash at best, and arguably a regression. `Spacewalk Thoughts` (ambient / chill) now outranks `Focus Flow` (lofi / focused). For a profile explicitly named around a genre, promoting a non-lofi track over a lofi one is the kind of move that only looks good if you believe mood matters more than genre — which is a defensible position, but the experiment didn't test it, because the mood weight never changed. The swap is really the *genre* cut doing the work, and it illustrates the cost side of that cut.

The two unchanged profiles are the more telling result. Rock and folk each have exactly one matching song in the catalog, so after #1 there is no genre or mood signal left to re-weight — the tail was already sorted by energy alone, and multiplying energy by two preserves that order exactly. **Re-weighting cannot fix a sparsity problem.** `Ultraviolet Hours` (house / euphoric) still outranks `Iron Verdict` (metal / angry) for the intense-rock listener, which was the worst result in the original run and is untouched here.

**The side effect worth recording.** Scores at the bottom of each list rose sharply — the #5 pick went from 1.41/5.50 (26% of max) to 2.82/6.00 (47% of max) for High-Energy Pop, and from 1.90/5.50 (35%) to 3.29/6.00 (55%) for Acoustic Wind-Down. Those songs are no better matched than before; they match on nothing but energy, and energy is now worth double. So the change made the system's *weakest* recommendations look roughly twice as confident without improving them at all. The near-tie spread at the bottom of Acoustic Wind-Down also widened from 0.07 to 0.15 points, which makes an essentially arbitrary ordering look more deliberate than it is.

**Takeaway.** Weight tuning moved exactly the rankings where two real signals were competing, and did nothing where only one signal existed. It corrected one known bias and introduced a new presentation problem — inflated confidence on filler results. The more valuable next change is not another weight but a minimum-score threshold, so that a 2.82 energy-only match is labelled weak rather than listed as the 5th-best song in the catalog.

*To revert:* set `GENRE_POINTS = 2.0` and `ENERGY_POINTS = 1.5` in `recommender.py`; `MAX_SCORE` and the `main.py` display follow automatically.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

**How recommenders turn data into predictions.** A recommendation is just a number attached to every item, sorted. That is the whole mechanism. What varies between systems is where the number comes from — mine adds up points for stated preferences, while Spotify infers it from the behavior of millions of listeners — but the final step is identical: score everything, sort, cut at K. Building the simple version made clear how much work that sort is quietly doing. Putting songs in an order *looks* like judgment even when nothing judged anything, and attaching a reason to each one ("genre match: lofi") looks like understanding even though the reasons are only a log of which if-statements fired. The system never predicts that you will enjoy a song. It predicts that the song matches a description, and the interface lets you read that as the same thing.

**Where bias and unfairness show up.** I expected bias to live in the weights, so I tuned them. It mostly lived in the data. Halving the genre weight changed nothing for two of my four profiles, because 13 of the 15 genres in the catalog have exactly one song — there was no signal left to re-weight. The clearest unfairness was subtler still: the energy formula measures distance on a 0–1 scale while the catalog only spans 0.22–0.97, so a listener wanting moderate energy is never far from anything and their preference barely affects the ranking, while listeners at the extremes get a signal that genuinely sorts the catalog. Nothing in that code treats anyone differently. The gap between what the formula assumes and what the data contains is what creates the unfairness, which makes it much harder to spot than a biased rule would be. The same shape of problem scales up: a real recommender trained on majority behavior will serve majority taste well and quietly offer everyone else a flatter, less useful signal, and the code will look neutral the whole time.

A fuller reflection on the engineering process — what AI tooling helped with, where I had to verify it, and what I would build next — is in [§ 10 of the Model Card](model_card.md#10-personal-reflection).



