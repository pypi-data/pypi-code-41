import pickle
class ChineseWordPiece:
    def __init__(self):
        self.spilt_diction = pickle.load(open('data/split.pkl', 'rb'))
        self.xinhua_diction = pickle.load(open('data/xinhua.pkl', 'rb'))
        self.pinyin = pickle.load(open('data/pinyin_list.pkl', 'rb'))
        self.exist_keys = self.spilt_diction.keys()
    def quiry(self, c_char):
        try:
            if c_char in self.exist_keys:
                return self.spilt_diction[c_char]
            else:
                return [self.xinhua_diction[c_char]['radicals'], self.xinhua_diction[c_char]['pinyin']]
        except:
            print('No such work %s' %c_char)
            return None
    def quiry_pinyin(self, c_char):
        try:
            return [self.xinhua_diction[c_char]['radicals'], self.xinhua_diction[c_char]['pinyin']]
        except:
            print('No such work %s' %c_char)
            return None
    def get_pinyin(self):
        return self.pinyin

