# core/config.py
"""Configuration constants and keywords for query classification and routing."""

# =============================================================================
# CASUAL KEYWORDS
# Messages containing these skip the RAG pipeline entirely
# =============================================================================
CASUAL_KEYWORDS = [
    # Greetings
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "greetings", "howdy", "what's up", "whats up", "sup",
    # Farewells
    "bye", "goodbye", "see you", "take care", "good night",
    # Gratitude
    "thank you", "thanks", "thank", "appreciate", "grateful",
    # Casual conversation
    "how are you", "how's it going", "nice to meet", "pleasure",
    # Simple responses
    "ok", "okay", "sure", "yes", "no", "got it", "understood",
    # Compliments
    "great", "awesome", "cool", "nice", "good job", "well done"
]

# =============================================================================
# TIME-SENSITIVE KEYWORDS
# Queries containing these trigger web search for fresh data
# =============================================================================
TIME_SENSITIVE_KEYWORDS = [
    "deadline", "last date", "when", "upcoming", "event", "events",
    "news", "announcement", "latest", "current", "today", "tomorrow",
    "this week", "this month", "schedule", "calendar", "holiday",
    "new", "update", "recently", "now", "open", "closed", "registration"
]

# =============================================================================
# INTENT CLASSIFICATION KEYWORDS
# Maps query terms to intent categories for better retrieval
# =============================================================================
INTENT_KEYWORDS = {
    "admissions": ["admission", "apply", "enroll", "entrance", "scholarship"],
    "undergraduate": ["undergraduate", "bachelor", "bba", "bs"],
    "graduate": ["graduate", "master", "mba", "ms", "phd"],
    "engineering_cs": ["engineering", "information technology", "IT", "CS", "SE", 
                       "computer science", "software engineering"],
    "business_natural": ["business", "economics", "natural sciences", "math", "physics"]
}

# =============================================================================
# UNCERTAINTY PHRASES
# If the LLM answer contains these, trigger fallback to web search
# =============================================================================
UNCERTAINTY_PHRASES = [
    "i don't know", "not sure", "no information",
    "cannot find", "don't have enough", "unable to find",
    "not mentioned", "no data"
]

# =============================================================================
# RESPONSE SETTINGS
# =============================================================================
MIN_CONTEXT_LENGTH = 50  # Minimum context length to proceed without fallback
MIN_ANSWER_LENGTH = 40   # Answers shorter than this may trigger escalation
