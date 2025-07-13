"""
Tests for name processing functionality.
"""

import unittest
import sys
import os

# Add src to path for imports (from tests/ folder perspective)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from poker_datamodel import Round, PlayerScore
from name_tools.name_clash_detector import _is_name_formatted_correct, _names_are_similar, detect_name_clashes
from poker_data_service.data_converter import _normalize_player_name


class TestNameNormalization(unittest.TestCase):
    """Test name normalization function."""
    
    def test_basic_normalization(self):
        """Test basic name cleaning and normalization."""
        self.assertEqual(_normalize_player_name("John Smith"), "john smith")
        self.assertEqual(_normalize_player_name("JANE DOE"), "jane doe")
        self.assertEqual(_normalize_player_name("Bob   Jones"), "bob jones")
    
    def test_special_characters_removal(self):
        """Test removal of special characters."""
        self.assertEqual(_normalize_player_name("John-Smith"), "johnsmith")
        self.assertEqual(_normalize_player_name("Jane.Doe"), "janedoe")
        self.assertEqual(_normalize_player_name("Bob's"), "bobs")
        self.assertEqual(_normalize_player_name("Mary@example"), "maryexample")
    
    def test_whitespace_handling(self):
        """Test proper whitespace handling."""
        self.assertEqual(_normalize_player_name("  John  Smith  "), "john smith")
        self.assertEqual(_normalize_player_name("John\tSmith"), "john smith")
        self.assertEqual(_normalize_player_name("John\nSmith"), "john smith")
        self.assertEqual(_normalize_player_name("John   Smith   Jr"), "john smith jr")
    
    def test_numbers_preserved(self):
        """Test that numbers are preserved in names."""
        self.assertEqual(_normalize_player_name("John Smith 2"), "john smith 2")
        self.assertEqual(_normalize_player_name("Player1"), "player1")
    
    def test_edge_cases(self):
        """Test edge cases for name normalization."""
        self.assertEqual(_normalize_player_name(""), "")
        self.assertEqual(_normalize_player_name("   "), "")
        self.assertEqual(_normalize_player_name("123"), "123")


class TestNameFormatValidation(unittest.TestCase):
    """Test name format validation functions."""
    
    def test_valid_names(self):
        """Test names that should be considered valid."""
        valid_names = [
            "john smith",
            "jane doe jr",
            "bob johnson",
            "mary jane watson",
            "player 1",
            "john 2"
        ]
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(_is_name_formatted_correct(name))
    
    def test_invalid_names(self):
        """Test names that should be considered invalid."""
        invalid_names = [
            "",           # Empty
            "   ",        # Whitespace only
            "john",       # Single word
            "j",          # Single character
            "123"         # Numbers only (single word)
        ]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(_is_name_formatted_correct(name))


class TestNameSimilarity(unittest.TestCase):
    """Test name similarity detection."""
    
    def test_similar_names(self):
        """Test names that should be considered similar."""
        similar_pairs = [
            ("john smith", "jon smith"),      # Typo in first name, same last name
            ("jane smith", "jan smith"),      # Very similar first names, same last name  
            ("kate jones", "katie jones"),    # One is nickname of other, same last name
        ]
        for name1, name2 in similar_pairs:
            with self.subTest(name1=name1, name2=name2):
                self.assertTrue(_names_are_similar(name1, name2))
    
    def test_dissimilar_names(self):
        """Test names that should NOT be considered similar."""
        dissimilar_pairs = [
            ("john smith", "john jones"),     # Different last initials
            ("john smith", "jane smith"),     # Different first names, same last
            ("mike brown", "sarah wilson"),   # Completely different
            ("mike jones", "michael jones"),  # Different enough first names (below 80% threshold)
            ("bob jones", "robert jones"),    # Different enough first names (below 80% threshold)
        ]
        for name1, name2 in dissimilar_pairs:
            with self.subTest(name1=name1, name2=name2):
                self.assertFalse(_names_are_similar(name1, name2))
    
    def test_edge_cases_similarity(self):
        """Test edge cases for name similarity."""
        # Malformed names should return False
        self.assertFalse(_names_are_similar("john", "jane"))
        self.assertFalse(_names_are_similar("", "john smith"))
        self.assertFalse(_names_are_similar("john smith", ""))


class TestNameClashDetection(unittest.TestCase):
    """Test name clash detection functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.rounds_with_issues = [
            Round(
                round_id="round1",
                bar_name="Test Bar",
                round_date="2025-07-01",
                players=(
                    PlayerScore("john", 100),        # Invalid: single name
                    PlayerScore("jane smith", 80),   # Valid
                    PlayerScore("jan smith", 70),    # Similar to jane smith (very close)
                )
            )
        ]
    
    def test_invalid_name_detection(self):
        """Test detection of invalid name formats."""
        clashes = detect_name_clashes(self.rounds_with_issues)
        
        # Should find the invalid name "john"
        invalid_name_clash = next((c for c in clashes if "Invalid name" in c and "john" in c), None)
        self.assertIsNotNone(invalid_name_clash)
        self.assertIn("Test Bar (2025-07-01)", invalid_name_clash)
    
    def test_similar_name_detection(self):
        """Test detection of similar names."""
        clashes = detect_name_clashes(self.rounds_with_issues)
        
        # Should find similar names "jane smith" and "jan smith"
        similar_name_clash = next((c for c in clashes if "Similar names" in c), None)
        self.assertIsNotNone(similar_name_clash)
        self.assertIn("jane smith", similar_name_clash)
        self.assertIn("jan smith", similar_name_clash)
        self.assertIn("Test Bar (2025-07-01)", similar_name_clash)
    
    def test_no_clashes_with_good_data(self):
        """Test that no clashes are detected with properly formatted data."""
        good_rounds = [
            Round(
                round_id="round1",
                bar_name="Test Bar", 
                round_date="2025-07-01",
                players=(
                    PlayerScore("alice smith", 100),
                    PlayerScore("bob jones", 80),
                    PlayerScore("charlie brown", 70),
                )
            )
        ]
        
        clashes = detect_name_clashes(good_rounds)
        self.assertEqual(len(clashes), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
