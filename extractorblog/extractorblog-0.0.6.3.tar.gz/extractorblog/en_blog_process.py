import nltk
nltk.download('punkt')
f = open('aa.txt', 'r', encoding='utf-8')
text = f.read()
f.close()



# sent_tokenize 文本分句处理，text是一个英文句子或文章
value = nltk.sent_tokenize(text)
# print(value)
# word_tokenize 分词处理,分词不支持中文
for i in value:
    words = nltk.word_tokenize(text=i)
    print(words)


nltk.download('averaged_perceptron_tagger')
# pos_tag 词性标注,pos_tag以一组词为单位，words是列表组成的词语列表
words = ['My', 'name', 'is', 'Lucy']
tags = nltk.pos_tag(words)
print(tags)



# 时态，过去词，进行时等
# 词语列表的时态复原，如果单词是全变形的无法识别
from nltk.stem import PorterStemmer

data = nltk.word_tokenize(text="worked presumably goes play,playing,played", language="english")
ps = PorterStemmer()
for w in data:
    print(w, ":", ps.stem(word=w))
# 单个词语的时态复原，如果单词是全变形的无法识别
from nltk.stem import SnowballStemmer

snowball_stemmer = SnowballStemmer('english')
a = snowball_stemmer.stem('plays')
print(a)

# 复数复原，如果单词是全变形的无法识别
from nltk.stem import WordNetLemmatizer

wordnet_lemmatizer = WordNetLemmatizer()
a = wordnet_lemmatizer.lemmatize('leaves')
print(a)


# 词干提取,提前每个单词的关键词，然后可进行统计，得出词频
from nltk.stem.porter import PorterStemmer

porter = PorterStemmer()
a = porter.stem('pets insurance')
print(a)

from nltk.corpus import wordnet

word = "good"


# 返回一个单词的同义词和反义词列表
def Word_synonyms_and_antonyms(word):
    synonyms = []
    antonyms = []
    list_good = wordnet.synsets(word)
    for syn in list_good:
        # 获取同义词
        for l in syn.lemmas():
            synonyms.append(l.name())
            # 获取反义词
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    return (set(synonyms), set(antonyms))


# 返回一个单词的同义词列表
def Word_synonyms(word):
    list_synonyms_and_antonyms = Word_synonyms_and_antonyms(word)
    return list_synonyms_and_antonyms[0]


# 返回一个单词的反义词列表
def Word_antonyms(word):
    list_synonyms_and_antonyms = Word_synonyms_and_antonyms(word)
    return list_synonyms_and_antonyms[1]


print(Word_synonyms(word))
print(Word_antonyms(word))


# 造句
print(wordnet.synset('name.n.01').examples())
# 词义解释
print(wordnet.synset('name.n.01').definition())



from nltk.corpus import wordnet

# 词义相似度.'go.v.01'的go为词语，v为动词
# w1 = wordnet.synset('fulfil.v.01')
# w2 = wordnet.synset('finish.v.01')
# 'hello.n.01'的n为名词
w1 = wordnet.synset('hello.n.01')
w2 = wordnet.synset('hi.n.01')
# 基于路径的方法
print(w1.wup_similarity(w2))  # Wu-Palmer 提出的最短路径
print(w1.path_similarity(w2))  # 词在词典层次结构中的最短路径
print(w1.lch_similarity(w2))  # Leacock Chodorow 最短路径加上类别信息
# 基于互信息的方法
from nltk.corpus import genesis

# 从语料库加载信息内容
# brown_ic = wordnet_ic.ic（'ic-brown.dat'）
# nltk自带的语料库创建信息内容词典
genesis_ic = wordnet.ic(genesis, False, 0.0)
print(w1.res_similarity(w2, genesis_ic))
print(w1.jcn_similarity(w2, genesis_ic))
print(w1.lin_similarity(w2, genesis_ic))
