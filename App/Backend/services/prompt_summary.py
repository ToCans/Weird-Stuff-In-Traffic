"""services/prompt_summary.py"""

# Imports
import spacy
from word2number import w2n

nlp = spacy.load("en_core_web_sm")

def extract_nouns_with_counts(user_prompt: str) -> list:
    """Extracts the nouns from the user prompt"""
    doc = nlp(user_prompt)
    results = []

    # Parsing through the document
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            count = 1
            for child in token.children:
                if child.pos_ == "NUM":
                    try:
                        # Try to parse as number (e.g., '2')
                        count = int(child.text)
                    except ValueError:
                        try:
                            # Try to parse as word-number (e.g., 'Two')
                            count = w2n.word_to_num(child.text.lower())
                        except:
                            count = 1  # fallback if it's not a valid number

            results.extend([token.lemma_] * count)

    return results
