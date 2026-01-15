#!/usr/bin/env python3
"""
Natural Language Processing Module for Consultation Summarizer
Provides text analysis functions for stakeholder feedback.
"""

from typing import Dict, List
from collections import Counter


def extract_key_phrases(comments: List[str], max_phrases: int = 20) -> List[Dict]:
    """
    Extract frequently occurring phrases from comments (simple word frequency).

    Args:
        comments: List of comment strings
        max_phrases: Maximum number of phrases to return

    Returns:
        List of phrase dicts with frequency
            [
                {'phrase': 'traffic congestion', 'count': 42, 'percentage': 14.2},
                ...
            ]
    """
    # Split into words and count
    word_counts = Counter()

    for comment in comments:
        # Simple word tokenization
        words = comment.lower().split()

        # Remove common words (simple stopwords)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

        filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
        word_counts.update(filtered_words)

    # Get top phrases
    total_comments = len(comments)
    phrases = []

    for word, count in word_counts.most_common(max_phrases):
        phrases.append({
            'phrase': word,
            'count': count,
            'percentage': round((count / total_comments) * 100, 1) if total_comments > 0 else 0
        })

    return phrases


def identify_emotion_indicators(comment: str) -> Dict:
    """
    Identify emotional indicators in a comment.

    Args:
        comment: Comment text

    Returns:
        Dict with emotion indicators
            {
                'anger': 2,
                'fear': 1,
                'frustration': 3,
                'support': 0
            }
    """
    comment_lower = comment.lower()

    # Emotion keyword patterns
    anger_keywords = ['angry', 'furious', 'outraged', 'disgusted', 'unacceptable']
    fear_keywords = ['scared', 'worried', 'afraid', 'concerned', 'anxious', 'nervous']
    frustration_keywords = ['frustrated', 'disappointed', 'tired of', 'fed up']
    support_keywords = ['excited', 'enthusiastic', 'supportive', 'pleased', 'happy']

    # Count matches
    anger_count = sum(1 for kw in anger_keywords if kw in comment_lower)
    fear_count = sum(1 for kw in fear_keywords if kw in comment_lower)
    frustration_count = sum(1 for kw in frustration_keywords if kw in comment_lower)
    support_count = sum(1 for kw in support_keywords if kw in comment_lower)

    return {
        'anger': anger_count,
        'fear': fear_count,
        'frustration': frustration_count,
        'support': support_count
    }


def calculate_reading_level(text: str) -> float:
    """
    Calculate approximate reading level using Flesch-Kincaid formula.

    Args:
        text: Text to analyze

    Returns:
        Grade level (approximate)
    """
    import re

    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])

    if sentence_count == 0:
        return 0.0

    # Count words
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0.0

    # Count syllables (rough approximation)
    syllable_count = 0
    for word in words:
        word = word.lower().strip('.,!?;:')
        syllables = max(1, len(re.findall(r'[aeiou]+', word)))
        syllable_count += syllables

    # Flesch-Kincaid Grade Level
    grade_level = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59

    return round(max(0, grade_level), 1)


def analyze_question_statements(comments: List[str]) -> Dict:
    """
    Categorize comments as questions vs. statements.

    Args:
        comments: List of comment strings

    Returns:
        Dict with question/statement analysis
            {
                'questions': 42,
                'statements': 58,
                'question_percentage': 42.0,
                'question_themes': ['When will construction start?', ...]
            }
    """
    questions = []
    statements = []

    for comment in comments:
        # Simple heuristic: contains '?' or starts with question word
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which', 'whose']

        if '?' in comment:
            questions.append(comment)
        elif any(comment.lower().startswith(qw) for qw in question_words):
            questions.append(comment)
        else:
            statements.append(comment)

    total = len(comments)

    return {
        'questions': len(questions),
        'statements': len(statements),
        'question_percentage': round((len(questions) / total) * 100, 1) if total > 0 else 0,
        'question_samples': questions[:5]  # First 5 questions
    }


def detect_suggestion_vs_concern(comment: str) -> str:
    """
    Classify comment as suggestion, concern, or neutral.

    Args:
        comment: Comment text

    Returns:
        Classification: 'suggestion', 'concern', 'neutral'
    """
    comment_lower = comment.lower()

    # Suggestion indicators
    suggestion_keywords = [
        'suggest', 'recommend', 'should', 'could', 'would be better',
        'propose', 'idea', 'consider', 'why not', 'what if'
    ]

    # Concern indicators
    concern_keywords = [
        'concern', 'worried', 'problem', 'issue', 'opposed',
        'disagree', 'negative', 'bad', 'harmful', 'dangerous'
    ]

    suggestion_score = sum(1 for kw in suggestion_keywords if kw in comment_lower)
    concern_score = sum(1 for kw in concern_keywords if kw in comment_lower)

    if suggestion_score > concern_score:
        return 'suggestion'
    elif concern_score > suggestion_score:
        return 'concern'
    else:
        return 'neutral'
