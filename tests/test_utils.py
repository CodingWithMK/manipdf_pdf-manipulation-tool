import pytest
from pathlib import Path
from manipdf.core.utils import parse_page_intervals

def test_parse_page_intervals_basic():
    assert parse_page_intervals("1, 3, 5", 10) == [0, 2, 4]
    assert parse_page_intervals("1-3, 5", 10) == [0, 1, 2, 4]

def test_parse_page_intervals_overlap():
    assert parse_page_intervals("1-5, 3-7", 10) == [0, 1, 2, 3, 4, 5, 6]

def test_parse_page_intervals_sorting():
    assert parse_page_intervals("10, 1-2, 5", 10) == [0, 1, 4, 9]

def test_parse_page_intervals_out_of_bounds():
    with pytest.raises(ValueError, match="Page 11 out of bounds"):
        parse_page_intervals("1, 11", 10)
    with pytest.raises(ValueError, match="Range 5-15 out of bounds"):
        parse_page_intervals("5-15", 10)

def test_parse_page_intervals_invalid_syntax():
    with pytest.raises(ValueError, match="Invalid page syntax"):
        parse_page_intervals("1, abc", 10)
    with pytest.raises(ValueError, match="Invalid range: 5-1"):
        parse_page_intervals("5-1", 10)

def test_parse_page_intervals_no_sort_no_dedup():
    assert parse_page_intervals("3, 2, 1", 10, sort_and_deduplicate=False) == [2, 1, 0]
    assert parse_page_intervals("1, 1, 2", 10, sort_and_deduplicate=False) == [0, 0, 1]
    assert parse_page_intervals("1-2, 1", 10, sort_and_deduplicate=False) == [0, 1, 0]

def test_parse_page_intervals_empty():
    assert parse_page_intervals("", 10) == []
    assert parse_page_intervals("  ", 10) == []
