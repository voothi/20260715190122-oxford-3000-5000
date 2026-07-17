#!/usr/bin/env python3
"""
ZID: 20260715190918
Description: Unit tests for the oxford-3000-5000 processing scripts.
             Imports modules from the sibling scripts directory (20260715190726).
"""

import sys
import os
import unittest
import importlib

# Add the sibling scripts directory to the python path
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, scripts_dir)

class TestOxfordScripts(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Dynamically import modules with numeric prefixes from scripts folder
        cls.m1 = importlib.import_module("1_create_corrected_oxford_5000")
        cls.m2 = importlib.import_module("2_clean_copy_paste_words")
        cls.m3 = importlib.import_module("3_move_homonym_digits")
        cls.m4 = importlib.import_module("4_apply_pos_level_pattern")
        cls.m5 = importlib.import_module("5_verify_pos_level")
        cls.m6 = importlib.import_module("6_sort_by_frequency")


    def test_clean_word_designations(self):
        clean_fn = self.m1.clean_word_designations
        self.assertEqual(clean_fn("hatred n,"), "hatred")
        self.assertEqual(clean_fn("terminal n  B2,"), "terminal")
        self.assertEqual(clean_fn("acid n. B2,"), "acid")
        self.assertEqual(clean_fn("counter (argue against)"), "counter (argue against)")
        self.assertEqual(clean_fn("  youngster  n.  C1  "), "youngster")

    def test_parse_line_to_word(self):
        parse_fn = self.m2.parse_line_to_word
        self.assertEqual(parse_fn("abolish v. C1"), "abolish")
        self.assertEqual(parse_fn("acid n. B2, adj. C1"), "acid")
        self.assertEqual(parse_fn("number A1, adv. A2"), "number")
        self.assertEqual(parse_fn("number n. A1, v. A2"), "number")
        self.assertIsNone(parse_fn("adj. A1, v. A2"))
        self.assertIsNone(parse_fn("v. A1"))

    def test_extract_digit(self):
        extract_fn = self.m3.extract_digit
        self.assertEqual(extract_fn("can1"), ("can", "1"))
        self.assertEqual(extract_fn("can2"), ("can", "2"))
        self.assertEqual(extract_fn("last1 (final)"), ("last (final)", "1"))
        self.assertEqual(extract_fn("second1 (next after the first)"), ("second (next after the first)", "1"))
        self.assertEqual(extract_fn("about"), ("about", ""))

    def test_extract_annotation_and_sense(self):
        fn = self.m1.extract_annotation_and_sense
        self.assertEqual(fn("bank (money)"), ("bank", "(money)", ""))
        self.assertEqual(fn("last1 (final)"), ("last", "(final)", "1"))
        self.assertEqual(fn("can1"), ("can", "", "1"))
        self.assertEqual(fn("second1 (next after the first)"), ("second", "(next after the first)", "1"))
        self.assertEqual(fn("about"), ("about", "", ""))

    def test_pos_level_parsing_pattern(self):
        get_pattern_fn = self.m4.get_parsed_pos_level_from_cp
        
        pos, lvl = get_pattern_fn("benefit n. A2, v. B1")
        self.assertEqual(pos, "n. A2, v. B1")
        self.assertEqual(lvl, "A2, B1")
        
        pos, lvl = get_pattern_fn("better adj. A1, adv. A2, n. B1")
        self.assertEqual(pos, "adj. A1, adv. A2, n. B1")
        self.assertEqual(lvl, "A1, A2, B1")
        
        pos, lvl = get_pattern_fn("bent adj. B2")
        self.assertEqual(pos, "adj.")
        self.assertEqual(lvl, "B2")
        
        pos, lvl = get_pattern_fn("bet v., n. B2")
        self.assertEqual(pos, "v., n.")
        self.assertEqual(lvl, "B2")
        
        pos, lvl = get_pattern_fn("about prep., adv. A1")
        self.assertEqual(pos, "prep., adv.")
        self.assertEqual(lvl, "A1")

    def test_clean_key(self):
        clean_k = self.m5.clean_key
        self.assertEqual(clean_k("content²"), "content")
        self.assertEqual(clean_k("bow'"), "bow")
        self.assertEqual(clean_k("well-being"), "wellbeing")
        self.assertEqual(clean_k("can2"), "can")

    def test_get_word_frequency_key(self):
        freq_key_fn = self.m6.get_word_frequency_key
        lemma_index = {"the": 0, "to": 1, "a": 2, "an": 3, "t-shirt": 4}
        
        # Test exact match
        self.assertEqual(freq_key_fn("the", lemma_index), (False, 0, "the"))
        
        # Test lowercase match
        self.assertEqual(freq_key_fn("The", lemma_index), (False, 0, "the"))
        
        # Test slash / comma separated match
        self.assertEqual(freq_key_fn("a, an", lemma_index), (False, 2, "a, an"))
        self.assertEqual(freq_key_fn("an/a", lemma_index), (False, 2, "an/a"))
        
        # Test fallback
        self.assertEqual(freq_key_fn("nonexistent", lemma_index), (True, 0, "nonexistent"))


if __name__ == "__main__":
    unittest.main()
