"""SEO Analyzer for AI Writing Automation

This module provides SEO analysis and recommendations for generated content.
"""

import re
from typing import NamedTuple
from dataclasses import dataclass


@dataclass
class SEOScore:
    """SEO analysis score data"""

    overall_score: float
    keyword_density: float
    heading_structure: float
    content_length: float
    keyword_in_title: bool
    keyword_in_headings: bool
    keyword_in_first_paragraph: bool
    readability_score: str
    details: dict


def analyze_seo(keyword: str, markdown_content: str) -> SEOScore:
    """Analyze SEO quality of markdown content

    Args:
        keyword: Target keyword to analyze for
        markdown_content: Markdown content to analyze

    Returns:
        SEOScore object with analysis results
    """
    # Normalize keyword
    normalized_keyword = keyword.lower().strip()

    # Extract content
    lines = markdown_content.split("\n")

    # Find title
    title = ""
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break

    # Extract headings
    headings = []
    for line in lines:
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            headings.append(heading)

    # Count word occurrences
    words = re.findall(r"\b\w+\b", markdown_content.lower())
    total_words = len(words)

    if total_words == 0:
        total_words = 1  # Avoid division by zero

    keyword_count = words.count(normalized_keyword)
    keyword_density = (keyword_count / total_words) * 100

    # Calculate individual scores
    keyword_in_title = normalized_keyword in title.lower()
    keyword_in_headings = any(normalized_keyword in heading.lower() for heading in headings)

    # Check first paragraph
    first_paragraph = ""
    for i, line in enumerate(lines):
        if not line.startswith("#") and line.strip():
            first_paragraph = line.strip()
            break

    keyword_in_first_paragraph = (
        normalized_keyword in first_paragraph.lower() if first_paragraph else False
    )

    # Calculate scores
    keyword_density_score = calculate_keyword_density_score(keyword_density)
    heading_structure_score = calculate_heading_structure_score(headings)
    content_length_score = calculate_content_length_score(total_words)
    title_score = 100 if keyword_in_title else 50
    heading_keyword_score = 100 if keyword_in_headings else 60
    first_paragraph_score = 100 if keyword_in_first_paragraph else 50

    # Overall score (weighted average)
    overall_score = (
        keyword_density_score * 0.25
        + heading_structure_score * 0.20
        + content_length_score * 0.20
        + title_score * 0.15
        + heading_keyword_score * 0.10
        + first_paragraph_score * 0.10
    )

    # Determine readability
    readability = determine_readability(total_words, len(markdown_content))

    # Build details
    details = {
        "total_words": total_words,
        "keyword_count": keyword_count,
        "heading_count": len(headings),
        "heading_levels": {"h1": 1, "h2": len([h for h in headings if not h.startswith("#")])},
        "title": title,
        "has_title": bool(title),
        "word_count_status": get_word_count_status(total_words),
    }

    return SEOScore(
        overall_score=round(overall_score, 1),
        keyword_density=round(keyword_density, 2),
        heading_structure=heading_structure_score,
        content_length=content_length_score,
        keyword_in_title=keyword_in_title,
        keyword_in_headings=keyword_in_headings,
        keyword_in_first_paragraph=keyword_in_first_paragraph,
        readability_score=readability,
        details=details,
    )


def calculate_keyword_density_score(density: float) -> float:
    """Calculate keyword density score

    Optimal density: 1-3%

    Args:
        density: Keyword density percentage

    Returns:
        Score out of 100
    """
    if density >= 1.0 and density <= 3.0:
        return 100.0
    elif density < 1.0:
        # Penalize low density
        return density * 100
    else:
        # Penalize high density (keyword stuffing)
        return max(0, 100 - (density - 3.0) * 20)


def calculate_heading_structure_score(headings: list[str]) -> float:
    """Calculate heading structure score

    Good structure has:
    - At least one H1
    - Multiple H2s
    - H3s under H2s (bonus)

    Args:
        headings: List of heading texts

    Returns:
        Score out of 100
    """
    if not headings:
        return 50.0

    # Count heading levels
    h1_count = 1  # First heading is always H1
    h2_count = 0

    for heading in headings[1:]:  # Skip first (H1)
        if heading.startswith("##"):
            h2_count += 1

    score = 50.0  # Base score for having headings

    # Bonus for H2s
    if h2_count >= 2:
        score += 30.0
    elif h2_count >= 1:
        score += 15.0

    # Bonus for heading count
    if len(headings) >= 5:
        score += 20.0
    elif len(headings) >= 3:
        score += 10.0

    return min(score, 100.0)


def calculate_content_length_score(word_count: int) -> float:
    """Calculate content length score

    Ideal length: 1000-2000 words

    Args:
        word_count: Total word count

    Returns:
        Score out of 100
    """
    if word_count >= 1000 and word_count <= 2000:
        return 100.0
    elif word_count >= 500 and word_count < 1000:
        return 70.0
    elif word_count >= 200 and word_count < 500:
        return 50.0
    elif word_count >= 2000:
        # Too long, might lose reader
        return 80.0
    else:
        # Too short
        return 30.0


def determine_readability(word_count: int, char_count: int) -> str:
    """Determine readability grade

    Args:
        word_count: Total word count
        char_count: Total character count

    Returns:
        Readability grade (A, B, C, D, F)
    """
    avg_word_length = char_count / word_count if word_count > 0 else 0

    if word_count >= 1000 and avg_word_length >= 4:
        return "A"
    elif word_count >= 500 and avg_word_length >= 4:
        return "B"
    elif word_count >= 300:
        return "C"
    elif word_count >= 100:
        return "D"
    else:
        return "F"


def get_word_count_status(word_count: int) -> str:
    """Get word count status description

    Args:
        word_count: Total word count

    Returns:
        Status description
    """
    if word_count >= 2000:
        return "Long (2000+ words)"
    elif word_count >= 1000:
        return "Optimal (1000-1999 words)"
    elif word_count >= 500:
        return "Moderate (500-999 words)"
    else:
        return "Short (<500 words)"


def get_seo_recommendations(score: SEOScore) -> list[str]:
    """Get SEO recommendations based on analysis

    Args:
        score: SEOScore object

    Returns:
        List of recommendations
    """
    recommendations = []

    # Keyword density
    if score.keyword_density < 1.0:
        recommendations.append(
            f"キーワード密度が低いです（{score.keyword_density}%）。"
            f"1-3%にするためにキーワードを追加してください。"
        )
    elif score.keyword_density > 3.0:
        recommendations.append(
            f"キーワード密度が高いです（{score.keyword_density}%）。"
            f"スパムとみなされる可能性があるため減らしてください。"
        )

    # Title
    if not score.keyword_in_title:
        recommendations.append("タイトルにキーワードを含めてください。")

    # Headings
    if not score.keyword_in_headings:
        recommendations.append("見出しにキーワードを含めてください。")

    if score.heading_structure < 70:
        if score.details.get("heading_count", 0) < 3:
            recommendations.append("見出しを追加してください。少なくとも3つの見出しを推奨します。")
        else:
            recommendations.append("見出し構造を改善してください。H2見出しを追加してください。")

    # Content length
    if score.content_length < 70:
        recommendations.append(
            f"コンテンツが短いです（{score.details.get('total_words', 0)}語）。"
            f"1000語以上を目指してください。"
        )

    # First paragraph
    if not score.keyword_in_first_paragraph:
        recommendations.append("最初の段落にキーワードを含めてください。")

    # General recommendations
    if score.overall_score >= 80:
        recommendations.append("🎉 SEOスコアが優秀です！このまま公開してください。")
    elif score.overall_score >= 60:
        recommendations.append(
            "SEOスコアは良好です。上記の推奨事項を反映するとさらに良くなります。"
        )
    else:
        recommendations.append("SEOスコアを改善するために、上記の推奨事項を反映してください。")

    return recommendations
