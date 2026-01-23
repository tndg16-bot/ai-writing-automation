"""Tests for SEO Analyzer"""

import pytest

from ai_writing.core.seo_analyzer import (
    analyze_seo,
    get_seo_recommendations,
    calculate_keyword_density_score,
    calculate_heading_structure_score,
    calculate_content_length_score,
    determine_readability,
)


def test_analyze_seo_basic():
    """Test basic SEO analysis"""
    markdown = """
# AI副業で稼ぐ方法

AI副業は現代のトレンドです。この記事ではAI副業について詳しく説明します。

## 始め方

AI副業を始めるには、まず適切なツールを選ぶ必要があります。

## おすすめのツール

以下のツールがおすすめです。
"""
    result = analyze_seo("AI副業", markdown)

    assert result.keyword_in_title
    assert result.keyword_in_headings
    assert result.overall_score > 0
    assert result.overall_score <= 100
    assert result.details["total_words"] > 0


def test_keyword_density_calculation():
    """Test keyword density calculation"""
    # Optimal density (1-3%)
    markdown_ideal = "キーワード " * 10 + "その他の単語 " * 300
    result = analyze_seo("キーワード", markdown_ideal)
    assert 1.0 <= result.keyword_density <= 3.0

    # Low density
    markdown_low = "キーワード " * 1 + "その他の単語 " * 100
    result = analyze_seo("キーワード", markdown_low)
    assert result.keyword_density < 1.0

    # High density
    markdown_high = "キーワード " * 20 + "その他の単語 " * 50
    result = analyze_seo("キーワード", markdown_high)
    assert result.keyword_density > 3.0


def test_heading_structure_score():
    """Test heading structure scoring"""
    # Good structure
    headings_good = [
        "Introduction",
        "First Section",
        "Second Section",
        "Third Section",
        "Fourth Section",
        "Fifth Section",
    ]
    score = calculate_heading_structure_score(headings_good)
    assert score >= 80

    # Poor structure
    headings_poor = ["Introduction"]
    score = calculate_heading_structure_score(headings_poor)
    assert score < 70

    # No headings
    headings_none = []
    score = calculate_heading_structure_score(headings_none)
    assert score == 50


def test_content_length_score():
    """Test content length scoring"""
    # Optimal length
    score_optimal = calculate_content_length_score(1500)
    assert score_optimal == 100.0

    # Too short
    score_short = calculate_content_length_score(100)
    assert score_short < 50

    # Too long
    score_long = calculate_content_length_score(2500)
    assert score_long < 100


def test_readability_grading():
    """Test readability grading"""
    grade_a = determine_readability(1500, 6000)
    assert grade_a == "A"

    grade_b = determine_readability(600, 2400)
    assert grade_b == "B"

    grade_c = determine_readability(350, 1400)
    assert grade_c == "C"

    grade_d = determine_readability(150, 600)
    assert grade_d == "D"

    grade_f = determine_readability(50, 200)
    assert grade_f == "F"


def test_get_seo_recommendations():
    """Test SEO recommendations generation"""
    # Poor SEO score
    markdown_poor = "短いコンテンツ"
    score_poor = analyze_seo("キーワード", markdown_poor)
    recommendations = get_seo_recommendations(score_poor)
    assert len(recommendations) > 0
    assert any("1000語" in rec for rec in recommendations)

    # Good SEO score
    markdown_good = """
# キーワードで稼ぐ

キーワードについて説明します。

## 詳しく解説

キーワードの使い方について詳しく説明します。この記事は十分な長さがあります。

## まとめ

キーワードについてまとめました。
"""
    # Add more content to reach optimal length
    markdown_good += " " * 5000
    score_good = analyze_seo("キーワード", markdown_good)
    recommendations = get_seo_recommendations(score_good)
    assert len(recommendations) > 0


def test_keyword_in_title():
    """Test keyword in title detection"""
    markdown_with_keyword = "# AI副業ガイド\n\nAI副業について説明します。"
    result = analyze_seo("AI副業", markdown_with_keyword)
    assert result.keyword_in_title

    markdown_without_keyword = "# ガイド\n\nAI副業について説明します。"
    result = analyze_seo("AI副業", markdown_without_keyword)
    assert not result.keyword_in_title


def test_keyword_in_headings():
    """Test keyword in headings detection"""
    markdown_with_keyword = "# Guide\n\n## AI副業について\n\n説明します。"
    result = analyze_seo("AI副業", markdown_with_keyword)
    assert result.keyword_in_headings

    markdown_without_keyword = "# Guide\n\n## 概要\n\n説明します。"
    result = analyze_seo("AI副業", markdown_without_keyword)
    assert not result.keyword_in_headings


def test_keyword_density_score_function():
    """Test keyword density score calculation function"""
    # Optimal
    score_ideal = calculate_keyword_density_score(2.0)
    assert score_ideal == 100.0

    # Too low
    score_low = calculate_keyword_density_score(0.5)
    assert score_low < 100

    # Too high
    score_high = calculate_keyword_density_score(5.0)
    assert score_high < 100


def test_overall_score_range():
    """Test overall score is within valid range"""
    markdown = """
# AI副業

AI副業について説明します。この記事ではAI副業の始め方を紹介します。
"""
    result = analyze_seo("AI副業", markdown)
    assert 0 <= result.overall_score <= 100


def test_details_dict_structure():
    """Test details dictionary has required keys"""
    markdown = "# Guide\n\nContent here."
    result = analyze_seo("keyword", markdown)

    assert "total_words" in result.details
    assert "keyword_count" in result.details
    assert "heading_count" in result.details
    assert "title" in result.details
    assert "has_title" in result.details
    assert "word_count_status" in result.details


def test_empty_content():
    """Test analysis with empty content"""
    result = analyze_seo("keyword", "")
    assert result.details["total_words"] == 0
    assert not result.keyword_in_title
    assert result.overall_score < 50


def test_readability_score():
    """Test readability score assignment"""
    markdown = "# Guide\n\n" + "Content. " * 200
    result = analyze_seo("keyword", markdown)
    assert result.readability_score in ["A", "B", "C", "D", "F"]


def test_multiple_keywords_in_content():
    """Test content with multiple keyword mentions"""
    markdown = """
# AI副業ガイド

AI副業は素晴らしいです。AI副業を始めましょう。AI副業は現代のトレンドです。
AI副業についてもっと知りましょう。AI副業で稼ぎましょう。
"""
    result = analyze_seo("AI副業", markdown)
    assert result.details["keyword_count"] >= 4
    assert result.overall_score > 50
