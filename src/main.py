"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

from recommender import load_songs, recommend_songs

# Resolved from this file's location, so the script runs from any directory.
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


WIDTH = 64


def print_profile(user_prefs: dict) -> None:
    """Prints the taste profile the recommendations are based on."""
    print("=" * WIDTH)
    print("YOUR TASTE PROFILE".center(WIDTH))
    print("=" * WIDTH)
    print(f"  Favorite genre : {user_prefs['genre']}")
    print(f"  Favorite mood  : {user_prefs['mood']}")
    print(f"  Target energy  : {user_prefs['energy']:.2f}")
    print(f"  Likes acoustic : {'yes' if user_prefs.get('likes_acoustic') else 'no'}")


def print_recommendations(recommendations: list) -> None:
    """Prints each recommendation with its score and itemized reasons."""
    print()
    print("=" * WIDTH)
    print(f"TOP {len(recommendations)} RECOMMENDATIONS".center(WIDTH))
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f"  {rank}. {song['title']}")
        print(f"     {song['artist']}  |  {song['genre']} / {song['mood']}")
        print(f"     Score: {score:.2f} / 5.50")
        print("     Why:")
        for reason in explanation.split("; "):
            print(f"       - {reason}")

    print()
    print("=" * WIDTH)


def main() -> None:
    songs = load_songs(CSV_PATH)

    # Starter example profile
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    print()
    print_profile(user_prefs)
    print_recommendations(recommend_songs(user_prefs, songs, k=5))


if __name__ == "__main__":
    main()
