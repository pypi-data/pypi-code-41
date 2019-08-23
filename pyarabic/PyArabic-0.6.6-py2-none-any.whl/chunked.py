#!/usr/bin/python
# -*- coding=utf-8 -*-
#
"""
Arabic Named enteties recognation pyarabic.named
@author: Taha Zerrouki
@contact: taha dot zerrouki at gmail dot com
@copyright: Arabtechies,  Arabeyes,   Taha Zerrouki
@license: GPL
@date:2017/02/14
@version: 0.3
"""
from __future__ import absolute_import
import sys

if __name__ == '__main__':
    sys.path.append('../')
    import pyarabic.araby as araby
    import pyarabic.named_const as named_const
    import pyarabic.propernouns as propernouns
else:
    sys.path.append(__file__)    
    import araby
    import named_const
    import propernouns

       
ABDNAMED = (
u"عبد",
)
ALLAH_NAMES = (
u"الله",
u"الرحمن",
u"الودود",
)

# from number import *
DINENAMED = (
    u'شمس',
    u'تقي',
    u'علاء',
    u'نجم',
    u'نور',
    u'سيف',
)
class Chunked:
    """
    A general chunk class to detect phrases in many forms, like named, numbers, temporal, etc.
    """
    def __init__(self,):
        self.begintag = "NB"
        self.intertag = "NI"
        pass
    
    def detect_chunks(self, wordlist):
        """
        Detect named enteties words in a text and return positions of each phrase.

        Example:
            >>> detect_chunk(u"قال خالد بن رافع  حدثني أحمد بن عنبر عن خاله")
            ((1,3), (6,8))

        @param wordlist: wordlist
        @type wordlist: unicode list
        @return: list of numbers clause positions [(start,end),(start2,end2),]
        @rtype: list of tuple

        """
        started = False
        taglist = []
        previous = ""
        for i, word_voc in enumerate(wordlist):
            #save the original word with possible harakat if exist
            word = araby.strip_tashkeel(word_voc)
            if not started:
                # if the word is a start tag word
                # a word which is a start tag like proper noun or an indicator 
                # الكلمة السابقة ليست موسومة، لكن الكلمة الحالية تجعلها كذلك
                if self.is_middle_tuple_tag(word, previous):
                    taglist.pop()
                    taglist.append(self.begintag)                                       
                    taglist.append(self.intertag)                                     
                    started = True

                #:كلمة توسم بنفسها
                elif self.is_wordtag(word):
                    taglist.append(self.begintag)
                    started = True       
                elif self.is_starttag(word):
                   taglist.append(self.begintag)
                   started = True
                else:
                    taglist.append("0")                    
                    started = False
                
            else: # توجد سلسلة منطلقة
                # الكلمة السابقة ليست موسومة، لكن الكلمة الحالية تجعلها كذلك
                if self.is_middle_tuple_tag(word, previous):
                    taglist.append(self.intertag)

                #:كلمة توسم بنفسها
                elif self.is_wordtag(word):
                    taglist.append(self.intertag)
                # الكلمة لا تكون موسومة إلا إذا كانت مسبوقة
                elif self.is_middle_wordtag(word):
                    taglist.append(self.intertag)
                else:
                    taglist.append("0")
                    started = False;
            
            previous = word
        return taglist
    def is_starttag(self, word):
        """
        return if the word is a start tag
        @param word: the given word
        @type word: unicode
        """
        return False

    def is_wordtag(self, word):
        """
        return if the word is a word tag any where
        @param word: the given word
        @type word: unicode
        """
        return False

    def is_middle_wordtag(self, word):
        """
        return if the word is a word tag only if there is a chunk
        @param word: the given word
        @type word: unicode
        """
        return False

    def is_middle_tuple_tag(self, word, previous):
        """
        return if the word is a word tag only if there the previous word is an indicator
        @param word: the given word
        @type word: unicode
        """
        
        return False

    def extract_chunks(self, text, context = False):
        """
        Extract chunks words in a text.

        Example:
            >>> extract_chunk(u"قال خالد بن رافع  حدثني أحمد بن عنبر عن خاله")
            ("خالد بن رافع"، "أحمد بن عنبر ")

            >>> extract_chunks(u"تصدق عبد الله بن عمر بدينار", context=True)
            ("تصدق"، "عبد الله بن عمر"، "بدينار")

        @param text: input text
        @type text: unicode
        @return: named enteties words extracted from text
        @rtype: integer
        """
        phrases = []
        wordlist = araby.tokenize(text)
        positions = self.detect_positions(wordlist)

        for pos in positions:
            if len(pos) >= 2:
                if pos[0] <= len(wordlist) and pos[1] <= len(wordlist):
                    if pos[0]-1 >= 0:
                        previous = wordlist[pos[0]-1]
                    else: previous = u''
                    if pos[1]+1 < len(wordlist):
                        nextword = wordlist[pos[1]+1]
                    else: nextword = u''
                    if context :
                        phrases.append((previous, \
                        u' '.join(wordlist[pos[0]: pos[1]+1]), nextword))
                    else:
                        phrases.append(u' '.join(wordlist[pos[0]: pos[1]+1]))                        
        return phrases


    def detect_positions(self, wordlist):
        """
        Detect named enteties words in a text and return positions of each phrase.

        Example:
            >>> detect_positions(wordlist)
            ((1,3), (6,8))
        @param wordlist: wordlist
        @type wordlist: unicode list
        @return: list of numbers clause positions [(start,end),(start2,end2),]
        @rtype: list of tuple
        """
        positions = []
        start = -1
        end = -1
        taglist = self.detect_chunks(wordlist)
        for i, tag in enumerate(taglist):
            if tag == self.begintag:
                start = i
                end = i
            elif tag == self.intertag : 
                end = i;
                startnamed = -1
            elif start >= 0:
                    positions.append((start, end))
                    start = -1
                    end = -1
        # add the final phrases
        if start >= 0: #There are a previous number phrase.
            positions.append((start, end))
        return positions
    @staticmethod
    def get_previous_tag(word):
        """Get the word tags
        @param word: given word
        @type word: unicode
        @return: word tag
        @rtype: unicode
        """
        return ''

    @staticmethod
    def vocalize(wordlist, syn_tags=""):
        """ Vocalize a number words
        @param wordlist: words to vocalize
        @type wordlist: unicode list
        @param syn_tags: tags about the clause
        @type syn_tags: unicode
        @return: the vocalized wordlist.
        @rtype: unicode
        """
        return wordlist

    def pretashkeel(self, wordlist):
        """
        Detect chunk words in a text.
        @param wordlist: input text
        @type wordlist: unicode
        @return: wordlist with vocalized named clause
        @rtype: list
        """
        taglist = self.detect_chunks(wordlist)
        previous = ""
        vocalized_list = []
        chunk = []
        previous_tag = ""
        for word, tag in zip(wordlist, taglist):
            if tag in (self.begintag, self.intertag):
                chunk.append(word)
            else:
                if chunk:
                    #get the tag of previous word
                    previous_tag = self.get_previous_tag(previous)
                    vocalized = self.vocalize(chunk, previous_tag)
                    vocalized_list.extend(vocalized)
                    chunk = []
                vocalized_list.append(word)
                previous = word
        if chunk:
            #get the tag of previous word
            previous_tag = self.get_previous_tag(previous)
            vocalized = self.vocalize(chunk, previous_tag)
            vocalized_list.extend(vocalized)            

        return vocalized_list


class myNamed(Chunked):
    """
    A general chunk class to detect phrases in many forms, like named, numbers, temporal, etc.
    """
    def __init__(self,):
        self.begintag = "NB"
        self.intertag = "NI"
    
    def is_starttag(self, word):
        """
        return if the word is a start tag
        @param word: the given word
        @type word: unicode
        """
        key = word
        # if the word is precedded by a prefix, we extract the prefix and 
        if word[0] in (u'و', u'ف', u'ل', u'ب', u'ك'):
           key = word[1:]
        # كلمة ابن لا تأتي هكذا إلا في البداية
        if key in (u'ابن', ):
           return True
        # if the word is  a word tag or as a prefixed word
        if self.is_wordtag(key):
            return True
        
        return False

    def is_wordtag(self, word):
        """
        return if the word is a word tag any where
        @param word: the given word
        @type word: unicode
        """
        # some words
        if word in (u'ابن', u'بن', u'أبو', u'أبا', \
                u'أبي', u'عبد', u'عبيد', u'بنو', u'بني', u'بنت'):
            return True
        if self.is_proper_noun(word):
            return True
        return False

    def is_middle_wordtag(self, word):
        """
        return if the word is a word tag only if there is a chunk
        @param word: the given word
        @type word: unicode
        """
        if word.startswith(u'ال') and word.endswith(u'ي'):
            return True
        return False

    def is_middle_tuple_tag(self, word, previous):
        """
        return if the word is a word tag only if there the previous word is an indicator
        @param word: the given word
        @type word: unicode
        """
        if previous in (u'بن', u'ابن', u'أبو', u'أبا', \
           u'أبي', u'عبد', u'عبيد', u'بنو', u'بني', u'بنت'):
            return True
        elif word in (u'بن', u'بنت',):
            return True
        # أسماء الأعلام بالدين
        if previous:
            if previous[0] in (u'و', u'ف', u'ل', u'ب', u'ك'):
               previous = previous[1:]
            if previous in DINENAMED  and word in (u"الدين", u"الإسلام"):
                return True
            elif previous in ABDNAMED and word in ALLAH_NAMES:
                return True
        
        return False

    @staticmethod
    def get_previous_tag(word):
        """Get the word tags
        @param word: given word
        @type word: unicode
        @return: word tag
        @rtype: unicode
        """
        word = araby.strip_tashkeel(word)
        #~ tags = u''
        if word in named_const.NOUN_NASEB_LIST:
            return u'منصوب'
        elif word in named_const.JAR_LIST:
            return u'مجرور'
        elif word in named_const.RAFE3_LIST:
            return u'مرفوع'
        else:
            return u''

    @staticmethod
    def vocalize(wordlist, syn_tags=""):
        """ Vocalize a number words
        @param wordlist: words to vocalize
        @type wordlist: unicode list
        @param syn_tags: tags about the clause
        @type syn_tags: unicode
        @return: the vocalized wordlist.
        @rtype: unicode
        """
        newlist = []
        #~ prefix = u""
        #~ nextword = u""
        #detect tags
        # we can pass tags to this number word
        tags = syn_tags
        bin_count = 0
        for i, word in enumerate(wordlist):
            #save the original word with possible harakat if exist
            word_nm = araby.strip_tashkeel(word)
            # the first word can have prefixes
            if i == 0 and word_nm:
                # word to get majrour tag
                if word_nm in (u'أبي', u'بنو', u'آل', u'ابن',):
                    tags += u"مجرور"
                elif word_nm in (u'أبو', ):
                    tags += u"مرفوع"
                elif word_nm in (u'أبا', ):
                    tags += u"منصوب"
            # select vocalization
            if word_nm == u'بن':
                bin_count += 1
                #treat first bin according to tags
                if bin_count == 1:
                    if u'مجرور' in tags:
                        voc = u'بْنِ'
                    elif u'مرفوع' in tags:
                        voc = u'بْنُ'
                    elif u'منصوب' in tags:
                        voc = u'بْنَ'
                    else:
                        voc = u'بْن'
                else:
                    #  u'مجرور'
                    voc = u'بْنِ'
            #Todo Vocalize names
            else:
                voc = word
            newlist.append(voc)
        return newlist

    @staticmethod
    def is_proper_noun(word):
        """
        Test if the word is a proper noun
        @param word: given word
        @type word: unicode
        @return: True if is properword
        @rtype: Boolean
        """
        # return word in named_const.ProperNouns
        return word in propernouns.PROPER_NOUNS


if __name__ == '__main__':
    import named
    TEXTS = [
        u"وجد عبد الله بن عمر دينارا",
        u"جاء  خالد بن الوليد وقاتل مسيلمة بن حذام الكذاب في موقعة الحديقة",
        u'''روى أحمد بن عقيل الشامي عن أبي طلحة
     المغربي أنّ عقابا بن مسعود بن أبي سعاد قال''',
        u"قال مُحَمَّدُ بْنُ خَالِدُ بْنُ إسماعيل في حديثه",
        u"ِنْصَرَفْنَا إِلَى أَنَسُ بْنُ مَالِكَ الْحَديثِ",
        u"ِخرج عبد الرحمن بن عوف",
        u"ِخرج عبد الودود من المولد",
        u"ِمررت بعبد الودود بن عمرو",
        u"ِمررت بعبد الودود  في البيت",
        u"صرّح الأمير تشارلز الأول",
    ]
    for text1 in TEXTS:
        print "#######"
        positions_named = named.detect_named_position(text1.split(' '))
        print(positions_named)
        text1 = araby.strip_tashkeel(text1)


        result = named.pretashkeel_named(araby.tokenize(text1))
        print(u' '.join(result))

        word_list = araby.tokenize(text1)
        tag_list = named.detect_named(word_list)

        tuples = (zip(tag_list, word_list))
        for tup in tuples:
            print repr(tup).decode('unicode-escape').encode('utf8')
        print "***********"
        chunker = myNamed()
        tag_list2 = chunker.detect_chunks(word_list)
        print chunker.detect_positions(word_list)
        print repr(chunker.extract_chunks(text1)).decode('unicode-escape').encode('utf8') 
        print repr(chunker.extract_chunks(text1, True)).decode('unicode-escape').encode('utf8') 
        result = chunker.pretashkeel(word_list)
        print "tashkeel", (u' '.join(result))
        tuples = (zip(tag_list2, word_list))
        for tup in tuples:
            print repr(tup).decode('unicode-escape').encode('utf8')           


