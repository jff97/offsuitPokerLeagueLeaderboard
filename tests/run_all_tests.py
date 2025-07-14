"""
Test runner for all poker system tests.
Run this file to execute all test modules in the test suite.
"""

import unittest
import sys

# Import all test modules
from test_name_processing import (
    TestNameNormalization,
    TestNameFormatValidation, 
    TestNameSimilarity,
    TestNameClashDetection
)

from test_poker_analytics import (
    TestPercentileCalculation,
    TestPlayerRanking,
    TestLeaderboardBuilding
)




def create_test_suite():
    """Create a comprehensive test suite including all test classes."""
    suite = unittest.TestSuite()
    
    # Name processing tests
    suite.addTest(unittest.makeSuite(TestNameNormalization))
    suite.addTest(unittest.makeSuite(TestNameFormatValidation))
    suite.addTest(unittest.makeSuite(TestNameSimilarity))
    suite.addTest(unittest.makeSuite(TestNameClashDetection))
    
    # Analytics tests
    suite.addTest(unittest.makeSuite(TestPercentileCalculation))
    suite.addTest(unittest.makeSuite(TestPlayerRanking))
    suite.addTest(unittest.makeSuite(TestLeaderboardBuilding))
    
    return suite


def run_all_tests():
    """Run all tests with detailed output."""
    print("Running Poker System Test Suite")
    print("=" * 50)
    
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFAILURES: {len(result.failures)} test(s) failed")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nERRORS: {len(result.errors)} test(s) had errors")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
