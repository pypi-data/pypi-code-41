# coding=utf-8
""""
    Item Based Collaborative Filtering Recommender with Attributes (Item Attribute KNN)
    [Rating Prediction]

    Its philosophy is as follows: in order to determine the rating of User u on item m, we can find other movies that
    are similar to item m, and based on User u’s ratings on those similar movies we infer his rating on item m.
    However, instead of traditional ItemKNN, this approach uses a metadata or pre-computed similarity matrix.

"""

# © 2019. Case Recommender (MIT License)

from collections import defaultdict
import numpy as np

from caserec.recommenders.rating_prediction.itemknn import ItemKNN
from caserec.utils.process_data import ReadFile

__author__ = 'Arthur Fortes <fortes.arthur@gmail.com>'


class ItemAttributeKNN(ItemKNN):
    def __init__(self, train_file=None, test_file=None, output_file=None, metadata_file=None, similarity_file=None,
                 k_neighbors=30, as_similar_first=True, metadata_as_binary=False, metadata_similarity_sep='\t',
                 similarity_metric="cosine", sep='\t', output_sep='\t'):
        """
        Item Attribute KNN for Rating Prediction

        This algorithm predicts a rank for each user based on the similar items that he/her consumed,
        using a metadata or similarity pre-computed file

        Usage::

            >> ItemAttributeKNN(train, test, similarity_file=sim_matrix, as_similar_first=True).compute()
            >> ItemAttributeKNN(train, test, metadata_file=metadata, as_similar_first=False).compute()

        :param train_file: File which contains the train set. This file needs to have at least 3 columns
        (user item feedback_value).
        :type train_file: str, default None

        :param test_file: File which contains the test set. This file needs to have at least 3 columns
        (user item feedback_value).
        :type test_file: str, default None

        :param output_file: File with dir to write the final predictions
        :type output_file: str, default None

        :param metadata_file: File which contains the metadata set. This file needs to have at least 2 columns
        (item metadata).
        :type metadata_file: str, default None

        :param similarity_file: File which contains the similarity set. This file needs to have at least 3 columns
        (item item similarity).
        :type similarity_file: str, default None

        :param k_neighbors: Number of neighbors to use. If None, k_neighbor = int(sqrt(n_users))
        :type k_neighbors: int, default None

        :param as_similar_first: If True, for each unknown item, which will be predicted, we first look for its k
        most similar users and then take the intersection with the users that
        seen that item.
        :type as_similar_first: bool, default True

        :param metadata_as_binary: f True, the explicit value will be transform to binary
        :type metadata_as_binary: bool, default False

        :param metadata_similarity_sep: Delimiter for similarity or metadata file
        :type metadata_similarity_sep: str, default '\t'

        :param similarity_metric: Pairwise metric to compute the similarity between the items. Reference about
        distances: http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.distance.pdist.html
        :type similarity_metric: str, default cosine

        :param sep: Delimiter for input files file
        :type sep: str, default '\t'

        :param output_sep: Delimiter for output file
        :type output_sep: str, default '\t'

        """

        super(ItemAttributeKNN, self).__init__(train_file=train_file, test_file=test_file, output_file=output_file,
                                               k_neighbors=k_neighbors, as_similar_first=as_similar_first, sep=sep,
                                               output_sep=output_sep, similarity_metric=similarity_metric)

        self.recommender_name = 'Item Attribute KNN Algorithm'

        self.metadata_file = metadata_file
        self.similarity_file = similarity_file
        self.metadata_as_binary = metadata_as_binary
        self.metadata_similarity_sep = metadata_similarity_sep

    def init_model(self):
        """
        Method to fit the model. Create and calculate a similarity matrix by metadata file or a pre-computed similarity
        matrix

        """

        self.similar_items = defaultdict(list)

        # Set the value for k
        if self.k_neighbors is None:
            self.k_neighbors = int(np.sqrt(len(self.items)))

        if self.metadata_file is not None:
            metadata = ReadFile(self.metadata_file, sep=self.metadata_similarity_sep, as_binary=self.metadata_as_binary
                                ).read_metadata_or_similarity()

            self.matrix = np.zeros((len(self.items), len(metadata['col_2'])))

            meta_to_meta_id = {}
            for m, data in enumerate(metadata['col_2']):
                meta_to_meta_id[data] = m

            for item in metadata['col_1']:
                for m in metadata['dict'][item]:
                    self.matrix[self.item_to_item_id[item], meta_to_meta_id[m]] = metadata['dict'][item][m]

            # create header info for metadata
            sparsity = (1 - (metadata['number_interactions'] / (len(metadata['col_1']) * len(metadata['col_2'])))) * 100

            self.extra_info_header = ">> metadata:: %d items and %d metadata (%d interactions) | sparsity:: %.2f%%" % \
                                     (len(metadata['col_1']), len(metadata['col_2']), metadata['number_interactions'],
                                      sparsity)

            # Create similarity matrix based on metadata or similarity file. Transpose=False, because it is an
            # item x metadata matrix
            self.si_matrix = self.compute_similarity(transpose=False)

        elif self.similarity_file is not None:
            similarity = ReadFile(self.similarity_file, sep=self.metadata_similarity_sep, as_binary=False
                                  ).read_metadata_or_similarity()

            self.si_matrix = np.zeros((len(self.items), len(self.items)))

            # Fill similarity matrix
            for i in similarity['col_1']:
                for i_j in similarity['dict'][i]:
                    self.si_matrix[self.item_to_item_id[i], self.item_to_item_id[int(i_j)]] = similarity['dict'][i][i_j]

            # Remove NaNs
            self.si_matrix[np.isnan(self.si_matrix)] = 0.0

        else:
            raise ValueError("This algorithm needs a similarity matrix or a metadata file!")

        # Create original matrix user x item for prediction process
        self.create_matrix()

        for i_id, item in enumerate(self.items):
            self.similar_items[i_id] = sorted(range(len(self.si_matrix[i_id])),
                                              key=lambda k: -self.si_matrix[i_id][k])[1:self.k_neighbors + 1]
