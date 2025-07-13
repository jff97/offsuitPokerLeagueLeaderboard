"""
DEPRECATED: This file has been split into focused test modules.

Please use the following files instead:
- tests/test_name_processing.py - Name normalization, validation, and clash detection
- tests/test_poker_analytics.py - Percentile calculations, ranking, and leaderboards
- tests/run_all_tests.py - Run all tests with clean output

This file remains only for reference.
"""

import unittest
import sys
import os

# Add src to path for imports (from tests/ folder perspective)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from poker_datamodel import Round, PlayerScore
from poker_analytics import _calculate_percentile_rank, build_percentile_leaderboard
from name_tools.name_clash_detector import detect_name_clashes


class TestBrittleHardcodedData(unittest.TestCase):
    """Brittle test with hardcoded data to validate complete poker analytics process."""
    
    def test_hardcoded_poker_leaderboard_validation(self):
        """Test complete poker analytics process with known hardcoded data and expected results."""
        
        # Hardcoded tournament data - 3 rounds with specific results
        hardcoded_rounds = [
            Round(
                round_id="round_001",
                bar_name="Test Bar A",
                round_date="2025-07-01",
                players=(
                    PlayerScore("alice", 100),
                    PlayerScore("bob", 80),
                    PlayerScore("charlie", 60),
                    PlayerScore("dave", 40)
                )
            ),
            Round(
                round_id="round_002",
                bar_name="Test Bar B", 
                round_date="2025-07-02",
                players=(
                    PlayerScore("bob", 120),
                    PlayerScore("eve", 90),
                    PlayerScore("alice", 70),
                    PlayerScore("frank", 50),
                    PlayerScore("grace", 30)
                )
            ),
            Round(
                round_id="round_003",
                bar_name="Test Bar A",
                round_date="2025-07-03", 
                players=(
                    PlayerScore("charlie", 110),
                    PlayerScore("alice", 85),
                    PlayerScore("dave", 75)
                )
            )
        ]
        
        # Build leaderboard with min_rounds=1
        leaderboard = build_percentile_leaderboard(hardcoded_rounds, min_rounds_required=1)
        
        # Manually calculated expected results:
        # Round 1 (4 players): Alice=100% (1st), Bob=66.67% (2nd), Charlie=33.33% (3rd), Dave=0% (4th)
        # Round 2 (5 players): Bob=100% (1st), Eve=75% (2nd), Alice=50% (3rd), Frank=25% (4th), Grace=0% (5th)
        # Round 3 (3 players): Charlie=100% (1st), Alice=50% (2nd), Dave=0% (3rd)
        #
        # Player averages:
        # Alice: (100% + 50% + 50%) / 3 = 66.67%
        # Bob: (66.67% + 100%) / 2 = 83.34%
        # Charlie: (33.33% + 100%) / 2 = 66.67%
        # Dave: (0% + 0%) / 2 = 0%
        # Eve: 75% / 1 = 75%
        # Frank: 25% / 1 = 25%
        # Grace: 0% / 1 = 0%
        
        expected_results = {
            "alice": {"rounds": 3, "avg_percentile": 66.67},
            "bob": {"rounds": 2, "avg_percentile": 83.34},
            "charlie": {"rounds": 2, "avg_percentile": 66.67},
            "dave": {"rounds": 2, "avg_percentile": 0.0},
            "eve": {"rounds": 1, "avg_percentile": 75.0},
            "frank": {"rounds": 1, "avg_percentile": 25.0},
            "grace": {"rounds": 1, "avg_percentile": 0.0}
        }
        
        # Verify leaderboard structure
        self.assertEqual(len(leaderboard), 7, "Should have exactly 7 players")
        expected_columns = ["Player", "RoundsPlayed", "AveragePercentileRank"]
        self.assertListEqual(list(leaderboard.columns), expected_columns)
        
        # Verify each player's results match expected values
        for _, row in leaderboard.iterrows():
            player_name = row["Player"]
            self.assertIn(player_name, expected_results, f"Unexpected player: {player_name}")
            
            expected = expected_results[player_name]
            self.assertEqual(row["RoundsPlayed"], expected["rounds"],
                           f"{player_name} should have {expected['rounds']} rounds")
            self.assertAlmostEqual(row["AveragePercentileRank"], expected["avg_percentile"], places=1,
                                 msg=f"{player_name} should have {expected['avg_percentile']}% average percentile")
        
        # Verify all expected players are present
        leaderboard_players = set(leaderboard["Player"].tolist())
        expected_players = set(expected_results.keys())
        self.assertEqual(leaderboard_players, expected_players, "Player lists should match exactly")
        
        print(f"\n✅ Brittle test passed with {len(hardcoded_rounds)} rounds and {len(leaderboard)} players")
        print("All hardcoded expectations matched actual results")


class TestCriticalFunctionality(unittest.TestCase):
    """Test only the most critical poker system functionality."""
    
    def test_percentile_calculation_extremes(self):
        """Test percentile calculation for edge cases."""
        # First place should always be 100%
        self.assertEqual(_calculate_percentile_rank(1, 10), 100.0)
        self.assertEqual(_calculate_percentile_rank(1, 2), 100.0)
        
        # Last place should always be 0%
        self.assertEqual(_calculate_percentile_rank(10, 10), 0.0)
        self.assertEqual(_calculate_percentile_rank(2, 2), 0.0)
        
        # Single player gets 100%
        self.assertEqual(_calculate_percentile_rank(1, 1), 100.0)
    
    def test_name_clash_detection_critical(self):
        """Test critical name clash detection functionality."""
        problem_rounds = [
            Round(
                round_id="test_round",
                bar_name="Test Bar",
                round_date="2025-07-01",
                players=(
                    PlayerScore("john", 100),        # Invalid: single name
                    PlayerScore("jane doe", 80),     # Valid
                    PlayerScore("jon doe", 70),      # Similar to jane doe
                )
            )
        ]
        
        clashes = detect_name_clashes(problem_rounds)
        
        # Should detect problems
        self.assertGreater(len(clashes), 0, "Should detect name issues")
        
        # Should find invalid name
        invalid_found = any("Invalid name" in clash and "john" in clash for clash in clashes)
        self.assertTrue(invalid_found, "Should detect invalid single name")
        
        # Should find similar names
        similar_found = any("Similar names" in clash for clash in clashes)
        self.assertTrue(similar_found, "Should detect similar names")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
