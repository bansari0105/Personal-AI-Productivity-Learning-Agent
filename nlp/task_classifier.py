"""Semantic task classification using pre-trained models.

Uses word embeddings to classify tasks based on semantic similarity,
not just keyword matching.
"""

import numpy as np

# Task category definitions with description and example tasks
TASK_CATEGORIES_SEMANTIC = {
    "exercise": {
        "keywords": ["gym", "workout", "run", "walk", "yoga", "swim", "bike", "exercise", "fitness", "train", "lift"],
        "description": "physical activity and fitness",
        "examples": ["run", "workout", "exercise", "fitness", "training"],
        "default_duration": 60,
        "icon": "[exercise]",
    },
    "meal": {
        "keywords": ["breakfast", "lunch", "dinner", "eat", "meal", "cook", "cooking", "food", "snack", "prepare", "make", "bake", "grill", "fry"],
        "description": "eating and food preparation",
        "examples": ["eat", "cook", "prepare", "meal", "food"],
        "default_duration": 45,
        "icon": "[meal]",
    },
    "meeting": {
        "keywords": ["meeting", "call", "sync", "standup", "sync up", "conference", "discussion", "presentation"],
        "description": "discussions and communications with others",
        "examples": ["meeting", "call", "discuss", "talk", "presentation"],
        "default_duration": 60,
        "icon": "[meeting]",
    },
    "commute": {
        "keywords": ["commute", "drive", "travel", "trip", "transport", "bus", "train", "taxi"],
        "description": "transportation and travel",
        "examples": ["travel", "drive", "commute", "transport", "journey"],
        "default_duration": 30,
        "icon": "[commute]",
    },
    "study": {
        "keywords": ["study", "learn", "read", "research", "course", "tutorial", "documentation", "book"],
        "description": "learning and reading",
        "examples": ["study", "learn", "read", "research", "course"],
        "default_duration": 120,
        "icon": "[study]",
    },
    "work": {
        "keywords": ["code", "program", "develop", "write", "review", "debug", "test", "work", "implement"],
        "description": "work and professional tasks",
        "examples": ["code", "work", "develop", "implement", "write"],
        "default_duration": 90,
        "icon": "[work]",
    },
    "break": {
        "keywords": ["break", "rest", "relax", "pause", "coffee", "stretch"],
        "description": "rest and relaxation",
        "examples": ["break", "rest", "relax", "pause"],
        "default_duration": 15,
        "icon": "[break]",
    },
    "personal": {
        "keywords": ["shower", "bath", "brush", "hygiene", "groom", "dress"],
        "description": "personal care and grooming",
        "examples": ["shower", "bath", "hygiene", "groom"],
        "default_duration": 20,
        "icon": "[personal]",
    },
}


def get_word_embeddings():
    """Load pre-trained word embeddings (spaCy or fallback)."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_md")  # Medium model with word vectors
            return nlp
        except OSError:
            print("Info: spaCy model not found. Install with:")
            print("  python -m spacy download en_core_web_md")
            print("Using keyword fallback instead.")
            return None
    except ImportError:
        print("Info: spaCy not installed. Using keyword fallback.")
        return None


def semantic_similarity(text1, text2, nlp=None):
    """Calculate semantic similarity between two texts using embeddings."""
    if nlp is None:
        # Fallback to keyword matching
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        return len(words1 & words2) / max(len(words1), len(words2))

    try:
        doc1 = nlp(text1)
        doc2 = nlp(text2)

        # Check if documents have vectors
        if not doc1.has_vector or not doc2.has_vector:
            return 0.0

        # Return cosine similarity (0-1)
        return doc1.similarity(doc2)
    except Exception as e:
        print(f"Similarity calculation error: {e}")
        return 0.0


def classify_task_semantic(task_text: str, nlp=None) -> dict:
    """Classify a task using semantic similarity with category descriptions.

    Args:
        task_text: The task description
        nlp: spaCy model (optional, uses keyword fallback if None)

    Returns:
        Dictionary with classification results
    """
    task_lower = task_text.lower()

    # Score each category using semantic similarity
    category_scores = {}

    for category, info in TASK_CATEGORIES_SEMANTIC.items():
        # Combine description and examples for matching
        category_text = f"{info['description']} {' '.join(info['examples'])}"

        # Calculate similarity score
        similarity = semantic_similarity(task_text, category_text, nlp)

        # Also check for keyword matches as a secondary signal
        keyword_matches = sum(1 for kw in info["keywords"] if kw in task_lower)
        keyword_boost = min(0.3, keyword_matches * 0.15)  # Boost up to 0.3

        # Combine scores
        total_score = similarity + keyword_boost
        category_scores[category] = total_score

    # Sort by score
    if not category_scores or max(category_scores.values()) == 0:
        return {
            "category": "other",
            "confidence": 0.0,
            "default_duration": 60,
            "icon": "[task]",
            "all_categories": [],
            "method": "default"
        }

    # Best match
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    best_category, best_score = sorted_categories[0]

    # Normalize confidence to 0-1
    confidence = min(1.0, best_score)

    info = TASK_CATEGORIES_SEMANTIC[best_category]

    # All matches with confidence
    all_matches = []
    for cat, score in sorted_categories:
        if score > 0:
            conf = min(1.0, score)
            all_matches.append({
                "category": cat,
                "confidence": round(conf, 2),
                "icon": TASK_CATEGORIES_SEMANTIC[cat]["icon"],
                "score": round(score, 3)
            })

    method = "semantic" if nlp else "keyword"

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "default_duration": info["default_duration"],
        "icon": info["icon"],
        "all_categories": all_matches,
        "method": method
    }


# Initialize model globally
_nlp_model = get_word_embeddings()


def classify_task(task_text: str) -> dict:
    """Main classification function - uses semantic model if available."""
    return classify_task_semantic(task_text, _nlp_model)


if __name__ == "__main__":
    # Test the semantic classifier
    print("Semantic Task Classification Tests")
    print("=" * 70)

    test_tasks = [
        "Go to the gym for an hour",
        "Prepare lunch and eat with colleagues",
        "Team standup meeting",
        "Drive to the office",
        "Study machine learning online",
        "Write code and implement features",
        "Take a coffee break",
        "Shower and get dressed",
        "Random task",
        "Cook dinner and clean kitchen",
        "Run 5km",
        "Read a book about Python",
    ]

    print(f"Using model: {_nlp_model.meta['name'] if _nlp_model else 'keyword fallback'}\n")

    for task in test_tasks:
        result = classify_task(task)
        print(f"Task: {task}")
        print(f"  Primary: {result['category']} ({result['confidence']:.0%}) [{result['method']}]")

        if len(result['all_categories']) > 1:
            print(f"  Also detected:")
            for cat in result['all_categories'][1:3]:  # Show top 2 alternatives
                print(f"    - {cat['category']} ({cat['confidence']:.0%})")
        print()
