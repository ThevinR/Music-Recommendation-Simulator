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

Running `python src/main.py` against the 18-song catalog in `data/songs.csv`, using the starter profile (pop / happy / energy 0.80 / no acoustic preference):

```
Loaded songs: 18

================================================================
                       YOUR TASTE PROFILE
================================================================
  Favorite genre : pop
  Favorite mood  : happy
  Target energy  : 0.80
  Likes acoustic : no

================================================================
                     TOP 5 RECOMMENDATIONS
================================================================

  1. Sunrise City
     Neon Echo  |  pop / happy
     Score: 4.97 / 5.50
     Why:
       - genre match: pop (+2.0)
       - mood match: happy (+1.5)
       - energy 0.82 vs target 0.80 (+1.47)

  2. Gym Hero
     Max Pulse  |  pop / intense
     Score: 3.30 / 5.50
     Why:
       - genre match: pop (+2.0)
       - energy 0.93 vs target 0.80 (+1.30)

  3. Rooftop Lights
     Indigo Parade  |  indie pop / happy
     Score: 2.94 / 5.50
     Why:
       - mood match: happy (+1.5)
       - energy 0.76 vs target 0.80 (+1.44)

  4. Corner Store Kings
     Dial Tone Theo  |  hip hop / confident
     Score: 1.47 / 5.50
     Why:
       - energy 0.78 vs target 0.80 (+1.47)

  5. Night Drive Loop
     Neon Echo  |  synthwave / moody
     Score: 1.42 / 5.50
     Why:
       - energy 0.75 vs target 0.80 (+1.42)

================================================================
```

**Reading the results.** The top pick scores 4.97 of a possible 5.50 by hitting genre, mood, and energy at once. The more interesting result is the gap between #2 and #3: "Gym Hero" matches the genre but has an `intense` mood, while "Rooftop Lights" is `happy` but filed under `indie pop`. The genre weight of 2.0 pushes the mood mismatch above the near-miss genre match — a concrete instance of the genre over-prioritization and exact-string-matching biases described above. A listener asking for upbeat pop would arguably prefer #3.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

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

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



