# -*- coding: utf-8 -*-
import unittest
from am_num2word import Number2WordsConverter


class Number2WordConverterTest(unittest.TestCase):
    def test_to_words(self):
        
        
        converter:Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(23203)
        self.assertEqual(words, "ሃያ ሶስት ሺህ ሁለት መቶ ሶስት")
        words, coma_sep = converter.convert(437343)
        self.assertEqual(words,
                         "አራት መቶ ሰላሳ ሰባት ሺህ ሶስት መቶ አርባ ሶስት")
        words, coma_sep = converter.convert(43050703)
        self.assertEqual(words,
                         "አርባ ሶስት ሚሊዮን ሃምሳ ሺህ ሰባት መቶ ሶስት")

    def test_to_coma_separated(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(0)
        self.assertEqual(coma_sep,"0")
        
    def test_to_words_single_digit(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(0)
        self.assertEqual(words, "ዜሮ")
        words, coma_sep = converter.convert(1)
        self.assertEqual(words, "አንድ")
        words, coma_sep = converter.convert(2)
        self.assertEqual(words, "ሁለት")
        words, coma_sep = converter.convert(9)
        self.assertEqual(words, "ዘጠኝ")
    def test_to_words_double_digit(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(10)
        self.assertEqual(words, "አስር")
        words, coma_sep = converter.convert(19)
        self.assertEqual(words, "አስራ ዘጠኝ")
    def test_to_words_hundreds(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(200)
        self.assertEqual(words, "ሁለት መቶ")
        words, coma_sep = converter.convert(350)
        self.assertEqual(words, "ሶስት መቶ ሃምሳ")
        words, coma_sep = converter.convert(999)
        self.assertEqual(words, "ዘጠኝ መቶ ዘጠና ዘጠኝ")


    def test_to_words_thousends(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(5000)
        self.assertEqual(words, "አምስት ሺህ")
        words, coma_sep = converter.convert(1400)
        self.assertEqual(words, "አንድ ሺህ አራት መቶ")
        words, coma_sep = converter.convert(8670)
        self.assertEqual(words, "ስምንት ሺህ ስድስት መቶ ሰባ")
        words, coma_sep = converter.convert(12970)
        self.assertEqual(words, "አስራ ሁለት ሺህ ዘጠኝ መቶ ሰባ")
    
        words, coma_sep = converter.convert(972140)
        self.assertEqual(words, "ዘጠኝ መቶ ሰባ ሁለት ሺህ አንድ መቶ አርባ")
        words, coma_sep = converter.convert(500232)
        self.assertEqual(words, "አምስት መቶ ሺህ ሁለት መቶ ሰላሳ ሁለት")
        words, coma_sep = converter.convert(501232)
        self.assertEqual(words, "አምስት መቶ አንድ ሺህ ሁለት መቶ ሰላሳ ሁለት")

    def test_to_words_millions(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(1000000)
        self.assertEqual(words, "አንድ ሚሊዮን")
        words, coma_sep = converter.convert(1000001)
        self.assertEqual(words, "አንድ ሚሊዮን አንድ")
        words, coma_sep = converter.convert(1000010)
        self.assertEqual(words, "አንድ ሚሊዮን አስር")
        
        words, coma_sep = converter.convert(1000520)
        self.assertEqual(words, "አንድ ሚሊዮን አምስት መቶ ሃያ")
        
        words, coma_sep = converter.convert(1001520)
        self.assertEqual(words, "አንድ ሚሊዮን አንድ ሺህ አምስት መቶ ሃያ")

        words, coma_sep = converter.convert(1071520)
        self.assertEqual(words, "አንድ ሚሊዮን ሰባ አንድ ሺህ አምስት መቶ ሃያ")

        words, coma_sep = converter.convert(1671520)
        self.assertEqual(words,
                         "አንድ ሚሊዮን ስድስት መቶ ሰባ አንድ ሺህ አምስት መቶ ሃያ")

    def test_float_numbers(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(1000000.0)
        self.assertEqual(words, "አንድ ሚሊዮን ነጥብ ዜሮ")
        words, coma_sep = converter.convert(1000001.12)
        self.assertEqual(words, "አንድ ሚሊዮን አንድ ነጥብ አንድ ሁለት")
        words, coma_sep = converter.convert(1000010.4566, 3)
        self.assertEqual(words, "አንድ ሚሊዮን አስር ነጥብ አራት አምስት ሰባት")

        words, coma_sep = converter.convert(1000010.4566, 4)
        self.assertEqual(words,
                         "አንድ ሚሊዮን አስር ነጥብ አራት አምስት ስድስት ስድስት")
    def test_negative_Numbers(self):
        converter: Number2WordsConverter = Number2WordsConverter()
        words, coma_sep = converter.convert(-1000520)
        self.assertEqual(words, "ነጌትቭ አንድ ሚሊዮን አምስት መቶ ሃያ")
        words, coma_sep = converter.convert(-1001520)
        self.assertEqual(words,
                         "ነጌትቭ አንድ ሚሊዮን አንድ ሺህ አምስት መቶ ሃያ")
        words, coma_sep = converter.convert(-1071520)
        self.assertEqual(words,
                         "ነጌትቭ አንድ ሚሊዮን ሰባ አንድ ሺህ አምስት መቶ ሃያ")
        words, coma_sep = converter.convert(-1671520)
        self.assertEqual(words,
                         "ነጌትቭ አንድ ሚሊዮን ስድስት መቶ ሰባ አንድ ሺህ አምስት መቶ ሃያ")
