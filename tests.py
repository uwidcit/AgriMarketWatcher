import os
import sys

sys.path.append(os.path.abspath("."))


def test_fetcher_get_most_recent():
    from fetcher import get_most_recent

    results = get_most_recent()
    assert "monthly" in results and "daily" in results
    assert len(results["monthly"]) > 0
    assert len(results["daily"]) > 0


def test_fetch_fish_getMostRecentFish():
    from fetch_fish import get_most_recent_fish

    results = get_most_recent_fish()
    assert len(results) > 0


def test_pushserver_run():
    from pushserver import run

    results = run(notify=False)
    assert "crops" in results and "fish" in results
