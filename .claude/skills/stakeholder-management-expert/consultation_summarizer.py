#!/usr/bin/env python3
"""
Stakeholder Consultation Summarizer
Analyzes stakeholder feedback from public meetings and generates response strategy.

Usage:
    python consultation_summarizer.py <input_json_path> [--output <output_path>] [--format json|markdown]

Example:
    python consultation_summarizer.py samples/sample_1_station_public_meeting.json
    python consultation_summarizer.py input.json --output report.md --format markdown
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import shared utilities
from Shared_Utils.stakeholder_utils import (
    categorize_themes,
    sentiment_analysis,
    frequency_weighting,
    generate_response_strategy,
    commitments_matrix,
    extract_key_quotes
)
from Shared_Utils.report_utils import eastern_timestamp

# Import local modules
from modules.validators import validate_input, validate_demographics, validate_output_options
from modules.nlp_processing import (
    extract_key_phrases,
    analyze_question_statements,
    detect_suggestion_vs_concern
)
from modules.output_formatters import format_markdown_report, format_json_output


def load_input(input_path: str) -> Dict:
    """
    Load and validate input JSON.

    Args:
        input_path: Path to input JSON file

    Returns:
        Input data dictionary

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input is not valid JSON
        ValueError: If input fails validation
    """
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_file, 'r') as f:
        data = json.load(f)

    # Validate input
    is_valid, error_msg = validate_input(data)
    if not is_valid:
        raise ValueError(f"Input validation failed: {error_msg}")

    # Validate optional sections
    if 'demographics' in data:
        is_valid, error_msg = validate_demographics(data['demographics'])
        if not is_valid:
            raise ValueError(f"Demographics validation failed: {error_msg}")

    if 'output_options' in data:
        is_valid, error_msg = validate_output_options(data['output_options'])
        if not is_valid:
            raise ValueError(f"Output options validation failed: {error_msg}")

    return data


def analyze_consultation(data: Dict, verbose: bool = False) -> Dict:
    """
    Perform complete consultation analysis.

    Args:
        data: Input data dictionary
        verbose: Print progress messages

    Returns:
        Dict with all analysis results
    """
    if verbose:
        print("Starting consultation analysis...")

    # Extract input components
    meeting_info = data['meeting_info']
    comments = data['comments']
    theme_categories = data['theme_categories']
    priorities = data.get('priorities', {})
    demographics = data.get('demographics', None)
    output_options = data.get('output_options', {})

    # Set defaults for priorities (all themes = priority 3 if not specified)
    for theme in theme_categories.keys():
        if theme not in priorities:
            priorities[theme] = 3

    results = {}

    # 1. Theme categorization
    if verbose:
        print(f"Categorizing {len(comments)} comments into {len(theme_categories)} themes...")

    categorization = categorize_themes(comments, theme_categories)
    results['categorization'] = categorization

    if verbose:
        print(f"  - Categorized: {categorization['statistics']['categorized_count']} comments")
        print(f"  - Uncategorized: {categorization['statistics']['uncategorized_count']} comments")
        print(f"  - Categories found: {categorization['statistics']['categories_found']}")

    # 2. Sentiment analysis
    if verbose:
        print("Analyzing sentiment...")

    sentiment = sentiment_analysis(comments)
    results['sentiment'] = sentiment

    if verbose:
        print(f"  - Overall sentiment: {sentiment['overall_sentiment']}")
        print(f"  - Support: {sentiment['sentiment_counts'].get('support', 0)}")
        print(f"  - Opposition: {sentiment['sentiment_counts'].get('opposition', 0)}")

    # 3. Frequency weighting
    if verbose:
        print("Calculating theme weights...")

    weighted_themes = frequency_weighting(categorization['categorized_feedback'])
    results['weighted_themes'] = weighted_themes

    if verbose:
        print(f"  - Top 3 themes:")
        for theme_data in weighted_themes['top_3_themes']:
            print(f"    {theme_data['rank']}. {theme_data['theme']} ({theme_data['count']} comments, {theme_data['percentage']}%)")

    # 4. Response strategies
    if verbose:
        print("Generating response strategies...")

    strategies = generate_response_strategy(
        categorization['categorized_feedback'],
        priorities
    )
    results['strategies'] = strategies

    if verbose:
        print(f"  - Generated {len(strategies)} response strategies")

    # 5. Commitments matrix
    if verbose:
        print("Extracting commitments...")

    include_commitments = output_options.get('include_commitments', True)
    if include_commitments:
        commitments = commitments_matrix(categorization['categorized_feedback'])
        results['commitments'] = commitments

        if verbose:
            print(f"  - Identified {len(commitments)} commitments")
    else:
        results['commitments'] = []

    # 6. Key quotes (if requested)
    include_quotes = output_options.get('include_quotes', True)
    max_quotes = output_options.get('max_quotes_per_sentiment', 5)

    if include_quotes:
        if verbose:
            print("Extracting key quotes...")

        # Get quotes by sentiment
        key_quotes = {}
        for sentiment_type in ['support', 'opposition', 'neutral']:
            quotes = extract_key_quotes(
                sentiment['sentiment_breakdown'],
                sentiment_filter=sentiment_type,
                limit=max_quotes
            )
            key_quotes[sentiment_type] = quotes

        results['key_quotes'] = key_quotes
    else:
        results['key_quotes'] = None

    # 7. Additional NLP analysis
    if verbose:
        print("Performing additional NLP analysis...")

    results['key_phrases'] = extract_key_phrases(comments)
    results['question_analysis'] = analyze_question_statements(comments)

    # Store input data
    results['meeting_info'] = meeting_info
    results['demographics'] = demographics

    if verbose:
        print("Analysis complete.")

    return results


def generate_report(results: Dict, output_format: str = 'markdown') -> str:
    """
    Generate final report in requested format.

    Args:
        results: Analysis results dictionary
        output_format: 'markdown' or 'json'

    Returns:
        Formatted report string
    """
    if output_format == 'json':
        return format_json_output(
            results['meeting_info'],
            results['categorization'],
            results['sentiment'],
            results['weighted_themes'],
            results['strategies'],
            results['commitments']
        )
    else:  # markdown
        return format_markdown_report(
            results['meeting_info'],
            results['categorization'],
            results['sentiment'],
            results['weighted_themes'],
            results['strategies'],
            results['commitments'],
            results['demographics'],
            results['key_quotes']
        )


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Stakeholder Consultation Summarizer - Analyze feedback and generate response strategy'
    )
    parser.add_argument(
        'input_json',
        type=str,
        help='Path to input JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: auto-generated in Reports/)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print progress messages'
    )

    args = parser.parse_args()

    try:
        # Load and validate input
        if args.verbose:
            print(f"Loading input from: {args.input_json}")

        data = load_input(args.input_json)

        # Override output format if specified in input
        if 'output_options' in data and 'output_format' in data['output_options']:
            output_format = data['output_options']['output_format']
        else:
            output_format = args.format

        # Perform analysis
        results = analyze_consultation(data, verbose=args.verbose)

        # Generate report
        if args.verbose:
            print(f"Generating {output_format} report...")

        report = generate_report(results, output_format)

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Auto-generate filename in Reports/
            timestamp = eastern_timestamp()
            meeting_date = data['meeting_info'].get('meeting_date', 'unknown')
            project_name = data['meeting_info'].get('project_name', 'consultation')
            project_slug = project_name.lower().replace(' ', '_')[:30]

            extension = 'json' if output_format == 'json' else 'md'
            filename = f"{timestamp}_consultation_summary_{project_slug}.{extension}"

            # Get project root (4 levels up from this script)
            project_root = Path(__file__).parent.parent.parent.parent
            output_path = project_root / 'Reports' / filename

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write output
        with open(output_path, 'w') as f:
            f.write(report)

        print(f"\nConsultation summary generated: {output_path}")

        # Print summary statistics
        print("\n--- Summary Statistics ---")
        print(f"Total Comments: {results['categorization']['statistics']['total_feedback']}")
        print(f"Themes Identified: {results['categorization']['statistics']['categories_found']}")
        print(f"Overall Sentiment: {results['sentiment']['overall_sentiment']}")
        print(f"Response Strategies: {len(results['strategies'])}")
        print(f"Commitments Tracked: {len(results['commitments'])}")

        # Print top 3 themes
        print("\nTop 3 Themes:")
        for theme_data in results['weighted_themes']['top_3_themes']:
            print(f"  {theme_data['rank']}. {theme_data['theme']} - {theme_data['count']} comments ({theme_data['percentage']}%)")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
