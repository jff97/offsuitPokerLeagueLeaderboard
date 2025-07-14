"""
Tests for poker analytics and ranking functionality.
Focuses on essential mathematical calculations and real API validation.
"""

import unittest
import sys
import os

from poker_scraper.datamodel import Round, PlayerScore
from poker_scraper.analytics import _calculate_percentile_rank, _rank_players_in_each_round, build_percentile_leaderboard


class TestPercentileCalculation(unittest.TestCase):
    """Test core percentile rank calculation."""
    
    def test_percentile_extremes_and_edge_cases(self):
        """Test percentile calculation for critical cases."""
        # First place should always be 100%
        self.assertEqual(_calculate_percentile_rank(1, 10), 100.0)
        self.assertEqual(_calculate_percentile_rank(1, 2), 100.0)
        
        # Last place should always be 0%
        self.assertEqual(_calculate_percentile_rank(10, 10), 0.0)
        self.assertEqual(_calculate_percentile_rank(2, 2), 0.0)
        
        # Single player gets 100%
        self.assertEqual(_calculate_percentile_rank(1, 1), 100.0)
        
        # Middle placement calculation - most important test
        # In a 10-person tournament, 5th place should be around 55.56%
        result = _calculate_percentile_rank(5, 10)
        self.assertAlmostEqual(result, 55.56, places=2)


class TestPlayerRanking(unittest.TestCase):
    """Test player ranking with ties."""
    
    def test_tie_handling_and_placement_skipping(self):
        """Test that tied players get same placement and subsequent placements skip correctly."""
        players = [
            PlayerScore("alice", 100),
            PlayerScore("bob", 80),
            PlayerScore("charlie", 100),  # Tie for first
            PlayerScore("dave", 60),
        ]
        round_obj = Round(
            round_id="test_round",
            bar_name="Test Bar",
            round_date="2025-07-01",
            players=tuple(players)
        )
        
        results = _rank_players_in_each_round([round_obj])
        
        # Find results for tied players (alice and charlie, both with 100 points)
        alice_result = next(r for r in results if r["Player"] == "alice")
        charlie_result = next(r for r in results if r["Player"] == "charlie")
        bob_result = next(r for r in results if r["Player"] == "bob")
        dave_result = next(r for r in results if r["Player"] == "dave")
        
        # Both tied players should have placement 1 and 100% percentile
        self.assertEqual(alice_result["Placement"], 1)
        self.assertEqual(charlie_result["Placement"], 1)
        self.assertEqual(alice_result["PercentileRank"], 100.0)
        self.assertEqual(charlie_result["PercentileRank"], 100.0)
        
        # Bob should be in 3rd place (after the two tied for 1st)
        self.assertEqual(bob_result["Placement"], 3)
        
        # Dave should be in 4th place
        self.assertEqual(dave_result["Placement"], 4)


class TestLeaderboardBuilding(unittest.TestCase):
    """Test leaderboard generation and mathematical validation."""
    
    def test_average_percentile_calculation(self):
        """Test that average percentiles are calculated correctly with simple test data."""
        # Round 1: Alice wins, Bob loses
        round1 = Round(
            round_id="round1",
            bar_name="Bar A",
            round_date="2025-07-01",
            players=(
                PlayerScore("alice", 100),
                PlayerScore("bob", 80),
            )
        )
        
        # Round 2: Bob wins, Alice loses
        round2 = Round(
            round_id="round2", 
            bar_name="Bar B",
            round_date="2025-07-02",
            players=(
                PlayerScore("bob", 100),
                PlayerScore("alice", 80),
            )
        )
        
        rounds = [round1, round2]
        leaderboard = build_percentile_leaderboard(rounds, min_rounds_required=1)
        
        # Alice: 100% in round1, 0% in round2 = 50% average
        # Bob: 0% in round1, 100% in round2 = 50% average
        for _, row in leaderboard.iterrows():
            self.assertEqual(row["AveragePercentileRank"], 50.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
