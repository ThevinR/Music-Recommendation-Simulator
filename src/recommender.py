import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Reads the song CSV into a list of dicts, converting numeric fields to int/float."""
    INT_FIELDS = {"id", "tempo_bpm"}
    FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            song = {}
            for key, value in row.items():
                value = value.strip()
                if key in INT_FIELDS:
                    song[key] = int(float(value))
                elif key in FLOAT_FIELDS:
                    song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)

    print(f"Loaded songs: {len(songs)}")
    return songs

# EXPERIMENT (weight shift): genre halved 2.0 -> 1.0, energy doubled 1.5 -> 3.0.
# Mood and the acoustic bonus are unchanged. Max score moves 5.50 -> 6.00.
GENRE_POINTS = 1.0
MOOD_POINTS = 1.5
ENERGY_POINTS = 3.0
ACOUSTIC_POINTS = 0.5
ACOUSTIC_THRESHOLD = 0.6

# Energy closeness is in [0, 1], so every term is at its stated maximum here.
MAX_SCORE = GENRE_POINTS + MOOD_POINTS + ENERGY_POINTS + ACOUSTIC_POINTS

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against the user's preferences, returning (score, reasons)."""

    score = 0.0
    reasons: List[str] = []

    if song["genre"].lower() == user_prefs["genre"].lower():
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS:.1f})")

    if song["mood"].lower() == user_prefs["mood"].lower():
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS:.1f})")

    # Always awarded: closeness shrinks the points as the gap widens.
    target_energy = user_prefs["energy"]
    closeness = max(0.0, 1.0 - abs(song["energy"] - target_energy))
    energy_points = ENERGY_POINTS * closeness
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {target_energy:.2f} "
        f"(+{energy_points:.2f})"
    )

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_POINTS
        reasons.append(f"acoustic pick (+{ACOUSTIC_POINTS:.1f})")

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song and returns the top k as (song, score, explanation) tuples."""
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]

    # Highest score first; ties broken alphabetically so runs are reproducible.
    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["title"]))

    return [
        (song, score, "; ".join(reasons) if reasons else "no strong matches")
        for song, score, reasons in ranked[:k]
    ]
