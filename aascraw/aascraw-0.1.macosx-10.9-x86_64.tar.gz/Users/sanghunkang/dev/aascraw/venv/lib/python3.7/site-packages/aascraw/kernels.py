# - features which contributes to variance of contents


# - collect a data get by xpath(s) with highest rank and compare
#     structure remains same and contents are variant: there is a high probability this is what we wanted. We increase the rank of this key
#     otherwise: we deem it as uninteresting. We decrease the rank of this key.
#     (어떤 element를 찾았는데, 이것이 맞으면 수집을 하고, 맞지 않으면 무시한다.)

#     How xpath rank is calculated will be discussed later.

# Kernels may deal with single element of a result tuple, or the entire tuple itself.

import numpy as np

from functools import reduce
import ctypes

SIZE_XPATH_SET = 4
c_kernels = ctypes.CDLL("./aascraw/c_kernels.so")

# c_kernels.rank_tuple_vicinity.argtypes = (ctypes.c_float*4, )

c_kernels.rank_tuple_vicinity.argtypes = (ctypes.c_wchar_p * SIZE_XPATH_SET, )
# c_kernels.rank_tuple_vicinity.restype = ctypes.c_float
c_kernels.rank_tuple_vicinity.restype = ctypes.c_int

arr = ctypes.c_wchar_p * SIZE_XPATH_SET
parameter_array = arr(*["array", "of", "strings", "asdasd"])


# print(c_kernels.rank_tuple_vicinity(parameter_array))
# (xpath_set, existing_records)
# rank_tuple_vicinity = c_kernels.rank_tuple_vicinity  
def rank_tuple_vicinity(xpath_set, existing_records):

    # actions = xpath_set[i]["filterer_action"]
    filterer_actions = [xpath["filterer_action"] for xpath in xpath_set]
    # print(filterer_actions)
    c_xpath_set = (ctypes.c_wchar_p * SIZE_XPATH_SET)(*filterer_actions)

    print(len(filterer_actions))
    print(c_xpath_set)
    rank = c_kernels.rank_tuple_vicinity(c_xpath_set)
    print(rank)
    return rank




# I HAVE TO CONSIDER USING DECORATORS
def rank_tuple_consistency(new_record, existing_records):
    """
    This function returns an integer which indicates how much the relative sizes of contents is preserved.
    It is 0 if relative sizes of contents are perfectly different from previous records, 
    and it is 1 if relative sizes of contents are at exact average of previous records.
    """
    # - features which contributes to consistency of format
    #     tag types   ~ 100, consider all. there are
    #     attributes  ~ 200, for now, concentrate in most common 5
    #     content types ~ ?
    # print(new_record)
    
    # TAKE LOG TO TAKE INTO ACCOUNT THAT STRUCTURED DATA ARE SHORT, WHEREAS UNSTRUCTURED DATA ARE LENGTHY
    # length_array_existing_records = np.zeros(len(existing_records[0][2]))
    # for existing_record in existing_records:
    #     length_array_existing_records += [np.log(len(element)) for element in existing_record[2]]

    # length_array_existing_records = length_array_existing_records / len(existing_records)
    # length_array_new_record = [np.log(len(element)) for element in new_record[2]]
    
    # print(length_array_existing_records)
    # print(length_array_new_record)

    rank = 0
    return rank

# def rank_tuple_vicinity(xpath_set, existing_records):
#     # I MIGHT HAVE TO CONSIDER IMPLEMETING THIS PART WITH CPP
#     rank = 0
    
    
#     # print(xpath_set)
#     pos = 0
#     numer = 0
#     denom = 0
#     max_xpath = 0
#     # reduce(lambda x1, x2: max(len(x1), len(x2)), xpath_set)
#     i = 0
#     while i < len(xpath_set):
#         max_xpath = max(len(xpath_set[i]["filterer_action"]), max_xpath)
#         i += 1

#     while pos < max_xpath: #len(xpath_set[0]["filterer_action"]):
#         vertical_slice = [None]*len(xpath_set)

#         i = 0
#         while i < len(xpath_set):
#             if pos < len(xpath_set[i]["filterer_action"]):
#                 vertical_slice[i] = xpath_set[i]["filterer_action"][pos]
#             denom += 1 # MAYBE ADD ONLY WHEN TRUE
#             i += 1

#         matching_score = 1 # Minimum
#         i = 0
#         while i < len(xpath_set):
#             temp_matching_score = 1
#             c = vertical_slice[i]
#             j = 0
#             while j < len(xpath_set):
#                 if i!= j and c == vertical_slice[j]: # I THINK THIS OPERATION IS REDUNDANT
#                     temp_matching_score += 1
#                 j += 1

#             if matching_score < temp_matching_score:
#                 matching_score = temp_matching_score
#             i += 1
        
#         # print(vertical_slice)
#         numer += matching_score
#         pos += 1
        
#     # for xpath in xpath_set:
#     #     print(xpath["filterer_action"][:100])

#     print("Ranking vicinity", numer/denom)
#     return rank

# Elementwise kernels
def rank_consistency_by_datatype(new_record, existing_records):
    rank = 0
    # FOR NOW, ONLY STRING, NUMBER, AND DATETIME-LIKE IS CONSIDERED
    for element in new_record:
        element_type = str # Defaults to string
        try:
            int()
        except Error:
            # SOME DATATIME CONVERSION
            pass
        
    # COMPARE MEAN OF VECTORS OF EXISTING RECORDS?

    return rank

def rank_content_variance(new_record, existing_records, element_index, record_length):
    """
    This functions measures how much a new record is variant from previously collected records.
    It is 0 if it the new record is exactly the same with one of previously collected records,
    and it is 1 if the new record is completly different from previously collected records.
    """
    # FOR NOW, ANY DIFFERENCE IN CONTENT IS CONSIDERED SIGNIFICANT VARIANCE

    rank = np.zeros(record_length)
    
    rank[element_index] = 1
    for existing_record in existing_records: # IF existing_record[3]==element_id 
        if existing_record["crawled_data"] == new_record["crawled_data"]:
            rank[element_index] = 0
    return rank

def rank_content_length(new_record, existing_records, element_id, record_length):
    arr_existing_elements = [np.log(len(record["crawled_data"])) for record in existing_records if record["index"]==element_id]
    
    score_mean_existing_elements = np.mean(arr_existing_elements)
    score_new_record = np.log(len(new_record["crawled_data"]))
    
    rank = np.zeros(record_length)
    rank[element_id] = np.square(score_new_record - score_mean_existing_elements)
    return rank


# how xpath rank is calculated?
# A desired property that

# A function to find xpath rank is defined accordingly.



#     distance between x2v 
#     if within average (+ some buffer) distance -> include to the board
#     else reject



