#     reinforcement
#  
#             minimise structure variance
#             if addition to the community spoils the structure more than the tolerance level, we reject it.


import numpy as np

# The goal of Storage class is to give rewards to Deliver and Filterer so that they can optimise the selection of
# of xpaths.

def recurse(prefix, matrix, index):
    if index < len(matrix):
        candidate_tuples = []
        for candidate in matrix[index]:            
            # NOTE THE TYPE MUST BE TUPLE
            candidate_tuples = candidate_tuples + recurse(prefix + [candidate], matrix, index+1)
    else:
        candidate_tuples = [prefix]
    return candidate_tuples

class Storage():
    def __init__(self, schema_length, consistency_embedding_length, use_default_kernels):        
        self.records = []
        # {
        #     "deliverer_action": string, of format DELIVERER_ACTION,
        #     "filterer_action": string, of format FILTERER_ACTION,
        #     "crawled_data": string, some string extracted by filterer from html
        #     "index": integer, indicates which index the crawled data might have relevance in the defined schema
        #     "rank_delta": integer,
        # } 

        self.element_kernels = []
        self.tuple_kernels = []
        
        self.__schema_length = schema_length
        self.__consistency_embedding_length = consistency_embedding_length
        self.count = 1
        self.maximum_rank_delta = 1

        # Initialisation based on flag parameters
        if use_default_kernels==True:
            for i in range(self.__schema_length):
                self.add_element_kernel(SOME_KERNEL, i)
            self.add_tuple_kernel(SOME_KERNEL)


    def __calculate_elementwise_rank(self, records_being_evaluated):
        existing_records = self.__sample_existing_records()
        
        for record_being_evaluated in records_being_evaluated:
            elementwise_rank = np.zeros(self.__schema_length)
                    
            # Calculate rank based on each element
            for kernel, element_id in self.element_kernels:
                # NOTE MULTIPLY WEIGHT TO KERNEL
                elementwise_rank += kernel(record_being_evaluated, existing_records, element_id, self.__schema_length)

            record_being_evaluated["rank_delta"] = elementwise_rank
            # print(record_being_evaluated)
        return records_being_evaluated

    def __calculate_tuplewise_rank(self, tuple_sample, results):
        # FIND A SET OF XPATHS WHICH BRINGS OUT MOST SIMILAR RANK VECTOR TO SAMPLE
        # Calculate rank based on tuple
        tuplewise_rank_delta = np.zeros(self.__consistency_embedding_length)
        existing_records = self.__sample_existing_records()
        
        for xpath_set in tuple_sample:
            for kernel in self.tuple_kernels:
                tuplewise_rank_delta += kernel(xpath_set, existing_records)

        return tuplewise_rank_delta

    def __sample_tuple(self, records):
        # The purpose of this selection is to set contraint of computaional complexity.
        # SORT AND SELECT TOP N ELEMENTS FOR EACH ELEMENT IN ELEMENTWISE_RANK
        sample_size = 5
        tuple_sample = []
        
        # Select top N candidates for xpath sets, ordered by rank delta
        for i in range(self.__schema_length):
            records_sorted_by_rank_delta = sorted(records, key=lambda x: x["rank_delta"][i])
            candidates_for_schema_i = records_sorted_by_rank_delta[:sample_size]
            tuple_sample.append(candidates_for_schema_i)
            
        # Combine candidates into sets
        result = recurse([], tuple_sample, 0)
        return result

    

    def __sample_existing_records(self):
        return self.records

    # Methods for setup
    def add_sample_data(self, sample_data, real_data=False):
        for sample_record in sample_data:
            for i, element in enumerate(sample_record):
                record = {
                    "deliverer_action": "HREF::SAMPLE_ACTION",
                    "filterer_action": "SAMPLE_ACTION",
                    "crawled_data": element,
                    "index": i,
                    "rank_delta": self.maximum_rank_delta,
                } 
                self.records.append(record)

    def add_element_kernel(self, kernel, element_index):
        if False: # NOTE ADD SAFETY CHECK FOR KERNEL FUNCTIONS
            raise Exception
        else:
            self.element_kernels.append((kernel, element_index))
        
    def add_tuple_kernel(self, kernel):
        if False: # NOTE ADD SAFETY CHECK FOR KERNEL FUNCTIONS
            raise Exception
        else:
            self.tuple_kernels.append(kernel)


    # Methods for exploration
    def evaluate_results(self, results, will_save=True):
        # Evaluate rank
        results = self.__calculate_elementwise_rank(results)
        tuple_sample = self.__sample_tuple(results)
        # print(len(tuple_sample))
        # for x in tuple_sample[0]:
        #     print(x)
        self.__calculate_tuplewise_rank(tuple_sample, results)
        #     # if will_save==True:
        #     #     self.records.append(result + [rank])    
        
    def get_rank_delta(self):
        # [action_master, rank_delta]
        return [], []