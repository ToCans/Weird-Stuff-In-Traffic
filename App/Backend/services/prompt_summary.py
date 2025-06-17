"""services/prompt_summary.py"""

# Imports
import spacy
from word2number import w2n

nlp = spacy.load("en_core_web_sm")

# Hardcoded container for words to exclude (background elements of a traffic scene)
EXCLUDE_WORDS = {
    "road", "street", "sidewalk", "pavement", "curb", "crosswalk", 
    "intersection", "traffic light", "sign", "building", "tree", 
    "bush", "grass", "sky", "cloud", "sun", "moon", "stars", "lamppost",
    "utility pole", "fire hydrant", "mailbox", "bench", "fence", "wall",
    "ground", "asphalt", "concrete", "gravel", "dirt", "path", "alley",
    "bridge", "tunnel", "overpass", "underpass", "river", "lake", "ocean",
    "mountain", "hill", "valley", "field", "park", "square", "plaza",
    "district", "neighborhood", "city", "town", "village", "suburb",
    "countryside", "horizon", "background", "foreground", "perspective",
    "atmosphere", "weather", "rain", "snow", "fog", "mist", "wind", "storm",
    "dusk", "dawn", "day", "night", "morning", "afternoon", "evening", "twilight"
}

def extract_nouns_with_counts(prompt):
    doc = nlp(prompt)
    results = []
    for token in doc:
        lemma_lower = token.lemma_.lower()
        
        # Only process if the token is a noun/proper noun AND not in the EXCLUDE_WORDS set
        if token.pos_ in ["NOUN", "PROPN"] and lemma_lower not in EXCLUDE_WORDS:
            count = 1
            for child in token.children:
                if child.pos_ == "NUM":
                    try:
                        count = int(child.text)
                    except ValueError:
                        try:
                            count = w2n.word_to_num(child.text.lower())
                        except:
                            count = 1
            results.extend([token.lemma_] * count)
    return results