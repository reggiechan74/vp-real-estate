#!/usr/bin/env python3
"""
Stakeholder Analysis Utilities Module
Provides shared functions for stakeholder feedback categorization, sentiment analysis,
frequency weighting, response strategy generation, and commitments tracking.

Used by:
- consultation_summarizer.py
- briefing_note_generator.py
"""

from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter
import re


def categorize_themes(
    feedback: List[str],
    categories: Dict[str, List[str]]
) -> Dict:
    """
    Categorize stakeholder feedback into themes using keyword matching.

    Args:
        feedback: List of feedback strings
            [
                "Concerned about traffic congestion during construction",
                "Property values will decline",
                "Need better pedestrian access",
                ...
            ]
        categories: Dict mapping category names to keyword lists
            {
                'Traffic': ['traffic', 'congestion', 'parking', 'road'],
                'Property Values': ['property value', 'assessment', 'market'],
                'Accessibility': ['access', 'pedestrian', 'wheelchair', 'bike'],
                ...
            }

    Returns:
        Dict containing theme categorization
            {
                'categorized_feedback': {
                    'Traffic': [
                        {'text': 'Concerned about...', 'index': 0},
                        ...
                    ],
                    'Property Values': [...],
                    ...
                },
                'uncategorized': [...],
                'multi_category': [...],  # Feedback matching multiple categories
                'statistics': {...}
            }
    """
    categorized = defaultdict(list)
    uncategorized = []
    multi_category = []

    for idx, comment in enumerate(feedback):
        comment_lower = comment.lower()
        matched_categories = []

        # Check against each category's keywords
        for category, keywords in categories.items():
            if any(keyword.lower() in comment_lower for keyword in keywords):
                matched_categories.append(category)
                categorized[category].append({
                    'text': comment,
                    'index': idx
                })

        # Track uncategorized and multi-category
        if len(matched_categories) == 0:
            uncategorized.append({'text': comment, 'index': idx})
        elif len(matched_categories) > 1:
            multi_category.append({
                'text': comment,
                'index': idx,
                'categories': matched_categories
            })

    # Calculate statistics
    total_feedback = len(feedback)
    categorized_count = sum(len(items) for items in categorized.values())

    return {
        'categorized_feedback': dict(categorized),
        'uncategorized': uncategorized,
        'multi_category': multi_category,
        'statistics': {
            'total_feedback': total_feedback,
            'categorized_count': categorized_count,
            'uncategorized_count': len(uncategorized),
            'multi_category_count': len(multi_category),
            'categories_found': len(categorized),
            'categorization_rate': round(
                (categorized_count / total_feedback) * 100, 1
            ) if total_feedback > 0 else 0
        }
    }


def sentiment_analysis(comments: List[str]) -> Dict:
    """
    Analyze sentiment (support, opposition, neutral, mixed) using keyword matching.

    Args:
        comments: List of comment strings

    Returns:
        Dict containing sentiment analysis
            {
                'sentiment_counts': {
                    'support': 15,
                    'opposition': 42,
                    'neutral': 8,
                    'mixed': 5
                },
                'sentiment_percentages': {...},
                'sentiment_breakdown': [
                    {'text': 'Great project!', 'sentiment': 'support'},
                    ...
                ]
            }
    """
    # Define sentiment keywords
    support_keywords = [
        'support', 'great', 'excellent', 'good', 'approve', 'favor',
        'positive', 'benefit', 'improve', 'love', 'like', 'excited',
        'appreciate', 'yes', 'agree'
    ]

    opposition_keywords = [
        'oppose', 'against', 'no', 'bad', 'terrible', 'concern', 'worried',
        'negative', 'harm', 'damage', 'destroy', 'ruin', 'hate', 'dislike',
        'disagree', 'unacceptable', 'unfair'
    ]

    neutral_keywords = [
        'question', 'clarify', 'understand', 'information', 'detail',
        'when', 'how', 'what', 'where'
    ]

    sentiment_breakdown = []
    sentiment_counts = Counter()

    for comment in comments:
        comment_lower = comment.lower()

        # Count keyword matches
        support_count = sum(1 for kw in support_keywords if kw in comment_lower)
        opposition_count = sum(1 for kw in opposition_keywords if kw in comment_lower)
        neutral_count = sum(1 for kw in neutral_keywords if kw in comment_lower)

        # Determine sentiment
        if support_count > 0 and opposition_count > 0:
            sentiment = 'mixed'
        elif support_count > opposition_count:
            sentiment = 'support'
        elif opposition_count > support_count:
            sentiment = 'opposition'
        elif neutral_count > 0:
            sentiment = 'neutral'
        else:
            # Default to neutral if no keywords matched
            sentiment = 'neutral'

        sentiment_counts[sentiment] += 1
        sentiment_breakdown.append({
            'text': comment,
            'sentiment': sentiment,
            'support_keywords': support_count,
            'opposition_keywords': opposition_count
        })

    # Calculate percentages
    total = len(comments)
    sentiment_percentages = {
        sentiment: round((count / total) * 100, 1) if total > 0 else 0
        for sentiment, count in sentiment_counts.items()
    }

    # Overall sentiment
    if sentiment_counts['opposition'] > sentiment_counts['support'] * 1.5:
        overall = 'Strong opposition'
    elif sentiment_counts['opposition'] > sentiment_counts['support']:
        overall = 'Moderate opposition'
    elif sentiment_counts['support'] > sentiment_counts['opposition'] * 1.5:
        overall = 'Strong support'
    elif sentiment_counts['support'] > sentiment_counts['opposition']:
        overall = 'Moderate support'
    else:
        overall = 'Mixed/neutral'

    return {
        'sentiment_counts': dict(sentiment_counts),
        'sentiment_percentages': sentiment_percentages,
        'sentiment_breakdown': sentiment_breakdown,
        'overall_sentiment': overall,
        'net_sentiment': sentiment_counts['support'] - sentiment_counts['opposition']
    }


def frequency_weighting(themes: Dict[str, List]) -> Dict:
    """
    Weight themes by frequency and intensity.

    Args:
        themes: Dict from categorize_themes()
            {
                'Traffic': [{'text': '...', 'index': 0}, ...],
                'Property Values': [...],
                ...
            }

    Returns:
        Dict containing weighted theme analysis
            {
                'weighted_themes': [
                    {'theme': 'Traffic', 'count': 42, 'weight': 0.35, 'rank': 1},
                    {'theme': 'Property Values', 'count': 28, 'weight': 0.23, 'rank': 2},
                    ...
                ],
                'top_3_themes': [...],
                'total_comments': 120
            }
    """
    # Count frequency of each theme
    theme_counts = {theme: len(comments) for theme, comments in themes.items()}
    total_comments = sum(theme_counts.values())

    # Calculate weights (frequency proportion)
    weighted_themes = []
    for theme, count in theme_counts.items():
        weight = count / total_comments if total_comments > 0 else 0
        weighted_themes.append({
            'theme': theme,
            'count': count,
            'weight': round(weight, 4),
            'percentage': round(weight * 100, 1)
        })

    # Sort by count (descending)
    weighted_themes.sort(key=lambda x: x['count'], reverse=True)

    # Add rank
    for rank, theme in enumerate(weighted_themes, start=1):
        theme['rank'] = rank

    # Identify top themes
    top_3_themes = weighted_themes[:3]

    return {
        'weighted_themes': weighted_themes,
        'top_3_themes': top_3_themes,
        'total_comments': total_comments,
        'num_themes': len(weighted_themes)
    }


def generate_response_strategy(
    themes: Dict[str, List],
    priorities: Dict[str, int]
) -> List[Dict]:
    """
    Generate response strategies for top concerns.

    Args:
        themes: Dict from frequency_weighting()
        priorities: Dict mapping theme to priority level (1-5, 1=highest)
            {'Traffic': 1, 'Property Values': 2, ...}

    Returns:
        List of response strategy recommendations
            [
                {
                    'theme': 'Traffic',
                    'priority': 1,
                    'comment_count': 42,
                    'strategy': 'Prepare detailed traffic management plan...',
                    'tactics': [...]
                },
                ...
            ]
    """
    # Standard response strategies by theme
    strategy_templates = {
        'Traffic': {
            'strategy': 'Prepare detailed traffic management plan and commit to mitigation measures',
            'tactics': [
                'Present traffic study with before/after analysis',
                'Commit to construction traffic routing away from residential streets',
                'Provide timeline for peak construction activities',
                'Establish complaint hotline for traffic issues'
            ]
        },
        'Property Values': {
            'strategy': 'Present market research and offer property value protection mechanisms',
            'tactics': [
                'Share comparable property studies showing minimal impact',
                'Explain appraisal process and fair market value determination',
                'Offer before/after valuations for affected properties',
                'Highlight project benefits (transit access, infrastructure)'
            ]
        },
        'Noise': {
            'strategy': 'Commit to noise monitoring and mitigation during construction',
            'tactics': [
                'Establish noise limits and monitoring program',
                'Restrict construction hours to daytime only',
                'Require noise barriers for high-impact areas',
                'Provide advance notice of high-noise activities'
            ]
        },
        'Accessibility': {
            'strategy': 'Enhance accessibility features and maintain access during construction',
            'tactics': [
                'Improve pedestrian crossings and sidewalks',
                'Ensure ADA compliance throughout project',
                'Maintain safe pedestrian routes during construction',
                'Add wayfinding signage and lighting'
            ]
        },
        'Business Impact': {
            'strategy': 'Minimize business disruption and provide support for affected businesses',
            'tactics': [
                'Phase construction to maintain access',
                'Provide advance notice of closures/changes',
                'Offer business liaison for concerns',
                'Consider compensation for proven losses'
            ]
        }
    }

    # Default strategy for themes without specific template
    default_strategy = {
        'strategy': 'Acknowledge concern and commit to ongoing communication',
        'tactics': [
            'Establish feedback mechanism',
            'Provide regular project updates',
            'Offer one-on-one meetings for affected parties',
            'Document commitments in writing'
        ]
    }

    # Generate strategies
    strategies = []
    for theme, comments in themes.items():
        priority = priorities.get(theme, 5)  # Default to low priority
        comment_count = len(comments)

        template = strategy_templates.get(theme, default_strategy)

        strategies.append({
            'theme': theme,
            'priority': priority,
            'comment_count': comment_count,
            'strategy': template['strategy'],
            'tactics': template['tactics']
        })

    # Sort by priority (1 = highest)
    strategies.sort(key=lambda x: x['priority'])

    return strategies


def commitments_matrix(feedback: Dict[str, List]) -> List[Dict]:
    """
    Extract and track commitments made during consultation.

    Args:
        feedback: Dict with categorized feedback and responses

    Returns:
        List of commitment tracking records
            [
                {
                    'theme': 'Traffic',
                    'commitment': 'No construction traffic on Main St',
                    'responsible_party': 'Project Team',
                    'deadline': 'Before construction starts',
                    'status': 'Pending',
                    'source': 'Public meeting #2'
                },
                ...
            ]
    """
    # Extract commitments from feedback using pattern matching
    commitment_patterns = [
        r'will\s+([^.]+)',
        r'commit\s+to\s+([^.]+)',
        r'ensure\s+([^.]+)',
        r'guarantee\s+([^.]+)',
        r'promise\s+([^.]+)'
    ]

    commitments = []

    for theme, comments in feedback.items():
        for comment_data in comments:
            comment = comment_data.get('text', '')

            # Search for commitment patterns
            for pattern in commitment_patterns:
                matches = re.findall(pattern, comment, re.IGNORECASE)
                for match in matches:
                    # Clean up the matched commitment
                    commitment_text = match.strip()

                    if len(commitment_text) > 10:  # Minimum length filter
                        commitments.append({
                            'theme': theme,
                            'commitment': commitment_text[:200],  # Cap length
                            'responsible_party': 'Project Team',  # Default
                            'deadline': 'TBD',
                            'status': 'Pending',
                            'source': f'Comment #{comment_data.get("index", 0) + 1}'
                        })

    return commitments


def extract_key_quotes(comments: List[Dict], sentiment_filter: Optional[str] = None, limit: int = 5) -> List[Dict]:
    """
    Extract key representative quotes from comments.

    Args:
        comments: List of comment dicts with sentiment
        sentiment_filter: Filter by sentiment ('support', 'opposition', 'neutral', 'mixed')
        limit: Maximum number of quotes to return

    Returns:
        List of key quotes
            [
                {'text': '...', 'sentiment': 'opposition', 'index': 42},
                ...
            ]
    """
    # Filter by sentiment if specified
    if sentiment_filter:
        filtered = [c for c in comments if c.get('sentiment') == sentiment_filter]
    else:
        filtered = comments

    # Sort by length (longer = more detailed)
    sorted_comments = sorted(filtered, key=lambda x: len(x.get('text', '')), reverse=True)

    # Return top N
    return sorted_comments[:limit]
