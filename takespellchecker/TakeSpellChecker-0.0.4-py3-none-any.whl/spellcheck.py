import math
import logging
import numpy as np
import pandas as pd
import multiprocessing
from gensim.models import Word2Vec
from pyjarowinkler import distance

class SpellCheck:
    
    def __init__(self, embedding_path: str, verbose: bool):
        self.__embedding = Word2Vec.load(embedding_path)
        self.__set_logging(verbose)
        self.data = None
            
    def __set_logging(self, verbose: bool):
        if verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)
            
    def set_data(self, data, content_column_name: str, file_sep: str = '|', encoding: str = 'utf-8'):
        self.data = data[content_column_name]
    
    def __calculate_limits(self, ind: int, sentence_len: int):
        left = ind - self.__window_limit
        right = ind + self.__window_limit
        left_limit = max(0, left)
        right_limit = min(sentence_len, right)
        return left_limit, right_limit
    
    def __find_correct_word(self, ind: int, left_limit: int, right_limit: int, sentence_lst: list):
        left_words = sentence_lst[left_limit:ind][::-1]
        right_words = sentence_lst[ind+1:right_limit]
        similar_words = self.__embedding.predict_output_word(left_words + right_words, topn = self.__context_candidates)
        similar_lst = [distance.get_jaro_distance(similar_word[0], sentence_lst[ind], winkler=False, scaling=0.1) for similar_word in similar_words]
        position = np.argmax(similar_lst)
        most_similar_word = similar_words[position][0] 
        return most_similar_word, max(similar_lst), position
    
    def __calculate_confiability_score(self, similarity: float, correct_position: int):
        return round(math.sqrt(pow(similarity, 3) * 0.85 / math.log10(correct_position + 8)),3)
    
    def spell_check_sentence(self, sentence: str):
        sentence_lst = sentence.split()
        mask_wrong = [False if word in self.__embedding.wv.vocab else True for word in sentence_lst]
        
        if True in mask_wrong:
            sentence_len = len(sentence_lst)
            for ind, value in enumerate(mask_wrong):
                if value:
                    left_limit, right_limit = self.__calculate_limits(ind,sentence_len)    
                    if False in mask_wrong[left_limit:right_limit]:    
                        most_similar_word, similarity_score, candidate_position = self.__find_correct_word(ind, left_limit, right_limit, sentence_lst)    
                        confiability_score = self.__calculate_confiability_score(similarity_score, candidate_position)
                        if confiability_score > self.__threshold:
                            sentence_lst[ind] = most_similar_word
                        
            return ' '.join(sentence_lst)
        return sentence
    
    def spell_check(self, window_limit: int = 5, threshold: float = 0.9, candidates: int = 10, save_result: bool = True, output_file_path: str = 'output_spell_check.csv'):
        logging.info('Starting spell check of {} sentences'.format(self.data.shape[0]))
        self.__threshold = threshold
        self.__window_limit = window_limit
        self.__context_candidates = candidates
    
        if self.data is not None:
            
            try:
                logging.info('Started spell checker sentences')
                with multiprocessing.Pool() as pool:
                    spell_checked_sentences = pool.map(self.spell_check_sentence, self.data)
                logging.info('Finished spell checker sentences')
                corrected = [True if spell_checked_sentences[ind] != sentence.strip() else False for ind, sentence in enumerate(self.data)]
            except Exception as e:
                logging.error('Spell checking error: {}'.format(e))
            else:
                result = pd.DataFrame({'Original': self.data, 'Spell Checked': spell_checked_sentences, 'Corrected': corrected})
                if save_result: 
                    logging.info('Saving spell checked file as {}'.format(output_file_path))
                    result.to_csv(output_file_path, sep = '|', encoding = 'utf-8', index=False)
                return result
            finally:
                logging.info('Finished spell check')
            
        else:
            logging.error('The text was not found. Use set_data to pass a string, list, series, dataframe or file path')