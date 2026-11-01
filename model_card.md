# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Think of the model as a judge handing out points at a talent show. Every song in the catalog walks on stage one at a time, the judge compares it against a short written description of what you like, and awards points for each thing it gets right. When every song has had its turn, they are lined up from most points to fewest, and the top five are handed back as recommendations. Nothing else happens — there is no memory of past rounds and no consulting with other judges.

**What the judge knows about you.** Four things, all of which you state outright: your favorite genre, your favorite mood, how energetic you want the music to be (a dial from calm to intense), and whether you have a soft spot for acoustic music. That is the entire profile. The model never watches what you actually listen to.

**What the judge knows about each song.** Each song in the catalog comes labeled with its genre, its mood, how energetic it is on that same calm-to-intense dial, and how acoustic it is. The catalog also records the artist, tempo, and a couple of other musical qualities, but the scoring ignores those for now.

**How the points are awarded.** A song earns two points for being in your favorite genre and one and a half points for matching your favorite mood. Energy works differently, because it is a dial rather than a label: instead of all-or-nothing, the song earns up to one and a half points depending on how close its energy is to the level you asked for. A perfect match earns the full amount, and the award shrinks steadily the further off it is, so a song that is slightly too mellow still earns most of the points while one that is wildly too intense earns almost none. Finally, if you said you like acoustic music and the song is genuinely acoustic, it picks up a half point bonus. The best a song can possibly do is five and a half points.

Those numbers are deliberate rather than arbitrary. Genre is weighted heaviest because it is the bluntest dealbreaker — a heavy metal track will not satisfy someone who asked for lo-fi, no matter how perfectly its energy lines up. Mood sits just behind it, because mood is the word people actually reach for when they describe what they want to hear. Energy is worth less on purpose: it is meant to break ties between songs that already match on genre and mood, not to overrule them. And the acoustic bonus stays small because it is a preference you mentioned, not a demand you made.

**Why every recommendation comes with reasons.** As the judge awards each point, they also jot down a note explaining it — "matches your favorite genre," "energy is close to what you asked for." Those notes are written at the exact moment the points are given, which means the explanation can never disagree with the score. If a song is recommended, you can see precisely which of your stated preferences earned it a place, and add up the points yourself if you doubt the result.

**What changed from the starter logic.** The starter version simply returned the first five songs in the file, in whatever order they happened to appear — the profile was ignored entirely. The working version scores all eighteen songs against the profile, ranks them, and explains each result. Two smaller decisions came out of testing: ties are broken alphabetically so that running the program twice gives identical output, and genre and mood are compared without regard to capitalization so that a stray capital letter in the catalog does not silently cost a song its points.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
