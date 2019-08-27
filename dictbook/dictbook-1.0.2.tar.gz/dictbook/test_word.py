s = ''' <ul class="base-list switch_part" class="">
                                                    <li class="clearfix">
                                <span class="prop">n.</span>
                                <p>
                                                                            <span>模式；</span>
                                                                            <span>花样，样品；</span>
                                                                            <span>图案；</span>
                                                                            <span>榜样，典范</span>
                                                                    </p>
                            </li>
                                                    <li class="clearfix">
                                <span class="prop">vt.</span>
                                <p>
                                                                            <span>模仿；</span>
                                                                            <span>以图案装饰；</span>
                                                                    </p>
                            </li>
                                                    <li class="clearfix">
                                <span class="prop">vi.</span>
                                <p>
                                                                            <span>形成图案；</span>
                                                                    </p>
                            </li>
                                            </ul>'''


from word import Word, WordList
from database import Database
import unittest

class WordTest(unittest.TestCase):

        def setUp(self):
                self.words = WordList()
                self.db = Database('d.db', 'words')
                self.w = Word('include')
        
        @unittest.skip
        def test_insert(self):
                self.db.insert(self.w.eng, str(self.w.meaning), '2019-8-27')

        def test_db(self):
                self.db.content()

        @unittest.skip
        def test_meaning(self):
                print(self.w.meaning)

        @unittest.skip
        def test_eng(self):
                print(self.w.eng)
        

if __name__ == "__main__":

        unittest.main()