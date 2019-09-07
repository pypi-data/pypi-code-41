import pandas as pd
import itertools
from domainNetwork.domain_network_utils import save_dataframe


class DomainNetwork:

    def __init__(self,
                 df,
                 nodes_list_to_remove,
                 min_edge_weight,
                 min_node_size,
                 min_stand_alone_size,
                 network_output_file_name,
                 netloc_output_file_name,
                 netloc_origin_output_file_name
                 ):
        self.df = df
        self.nodes_list_to_remove = nodes_list_to_remove
        self.min_edge_weight = min_edge_weight
        self.min_node_size = min_node_size
        self.min_stand_alone_size = min_stand_alone_size

        self.user_names = self.df.user_name.unique()

        """a dataframe of netlocs and the total number of times a netloc is mentioned """
        self.df_netlocs = pd.DataFrame(self.df[['url_netloc_clean']].groupby(['url_netloc_clean']).size().reset_index(name='count'))
        self.df_netlocs_origin = pd.DataFrame(self.df[['url_netloc_clean']].groupby(['url_netloc_clean']).size().reset_index(name='count'))

        print("self.df", self.df.shape)
        print("self.df_netlocs in init",self.df_netlocs.shape)
        self.df_network = None

        self.network_output_file_name = network_output_file_name
        self.netloc_output_file_name = netloc_output_file_name
        self.netloc_origin_output_file_name = netloc_origin_output_file_name


    def get_network_per_user(self, df_user_netloc, username):
        '''select netlocs mentioned by a specific user'''
        ntlc = list(df_user_netloc.loc[df_user_netloc['user_name'] == username, 'url_netloc_clean'])

        '''select all combination of two netlocs'''
        sub_2 = [subset for subset in itertools.combinations(ntlc, 2)]
        return sub_2

    def create_domain_network(self):
        """ create a groupby dataframe of users, netlocs and the count """
        df_user_netloc_count = (self.df.groupby(['user_name', 'url_netloc_clean']).size().reset_index(name='count'))

        """create a list of source target for all users"""
        netloc_s_t = sum((self.get_network_per_user(df_user_netloc_count, usr) for usr in self.user_names), [])

        """aggregate list of source targets and give the weights"""
        netloc_s_t = pd.DataFrame(netloc_s_t, columns=['source', 'target'])
        self.df_network = (netloc_s_t.groupby(['source', 'target']).size().reset_index(name='weight'))

        """Since groupby to create df_user_netloc_count, is alphabetically ordered by default, 
            it seems we do not endup with rows that source and target values are switched"""


    def combine_2nodes(self, node_to_replace, node_to_remove):
        replace_node_count = self.df_netlocs.loc[self.df_netlocs['url_netloc_clean'] == node_to_replace, 'count']
        remove_node_count = self.df_netlocs.loc[self.df_netlocs['url_netloc_clean'] == node_to_remove, 'count']

        replace_node_count_val = replace_node_count.values[0] if len(replace_node_count) > 0 else 0
        remove_node_count_val = remove_node_count.values[0] if len(remove_node_count) > 0 else 0

        self.df_netlocs.loc[self.df_netlocs['url_netloc_clean'] == node_to_replace, 'count'] = replace_node_count_val + remove_node_count_val
        self.df_netlocs = self.df_netlocs[self.df_netlocs.url_netloc_clean != node_to_remove]

    def combine_nodes(self, dict_change_netlocs):
        for key, value in dict_change_netlocs.items():
            node_to_replace = key
            node_to_remove = dict_change_netlocs[key]

            self. combine_2nodes(node_to_replace, node_to_remove)

        print("df_netlocs",self.df_netlocs.shape)

    def filter_by_node_size(self):
        count_filter = self.df_netlocs['count'] >= self.min_node_size
        self.df_netlocs = self.df_netlocs.loc[count_filter]

    def filter_nodes_to_remove(self):
        removing_netlocs_filter = self.df_netlocs['url_netloc_clean'].isin(self.nodes_list_to_remove)
        self.df_netlocs = self.df_netlocs.loc[~removing_netlocs_filter]

    def trim_nodes(self):
        self.filter_by_node_size()
        print("df_netlocs after filter by node size", self.df_netlocs.shape)
        self.filter_nodes_to_remove()
        print("self.df_netlocs after removing social .. ",self.df_netlocs.shape)

    def swap_source_target(self, cond):
        compare_filter = self.df_network['source'] > self.df_network['target']
        self.df_network.loc[compare_filter & cond, ['source', 'target']] = (
            self.df_network.loc[compare_filter & cond, ['target', 'source']].values)


    def replace_node_in_network(self, node_to_replace, node_to_remove):
        """Replace node_to_remove with node_to_replace in the network"""
        self.df_network.loc[self.df_network['source'] == node_to_remove, 'source'] = node_to_replace
        self.df_network.loc[self.df_network['target'] == node_to_remove, 'target'] = node_to_replace

        """Swap source and target if target < source alphabetically"""
        cond = (self.df_network['source'] == node_to_replace) | (self.df_network['target'] == node_to_replace)
        self.swap_source_target(cond)
        self.df_network = pd.DataFrame(self.df_network.groupby(['source', 'target']).sum()['weight']).reset_index()

    def replace_nodes_in_network(self, dict_change_netlocs):
        for key, value in dict_change_netlocs.items():
            node_to_replace = key
            node_to_remove = dict_change_netlocs[key]
            self. replace_node_in_network(node_to_replace, node_to_remove)

    def remove_edge_by_weight(self):
        weight_filter = self.df_network['weight'] >= self.min_edge_weight
        self.df_network = self.df_network[weight_filter]

    def remove_network_not_found_in_nodeList(self):
        """remove network of nodes that are not in node list.
        Including nodes< node_size and nodes in removing list """

        desired_node_list = list(self.df_netlocs['url_netloc_clean'])
        source_filter = self.df_network['source'].isin(desired_node_list)
        target_filter = self.df_network['target'].isin(desired_node_list)
        self.df_network = self.df_network[source_filter & target_filter]

    def trim_domain(self):
        self.remove_edge_by_weight()
        self.remove_network_not_found_in_nodeList()

    def find_stand_alone_nodes(self):
        source_filter = self.df_netlocs['url_netloc_clean'].isin(self.df_network['source'])
        target_filter = self.df_netlocs['url_netloc_clean'].isin(self.df_network['target'])
        nodesize_filter = self.df_netlocs['count'] >= self.min_stand_alone_size

        stand_alone_netlocs = list(self.df_netlocs.loc[~source_filter & ~target_filter,'url_netloc_clean'])
        popular_stand_alone_netlocs = list(self.df_netlocs.loc[~source_filter & ~target_filter & nodesize_filter, 'url_netloc_clean'])
        return stand_alone_netlocs,popular_stand_alone_netlocs


    def add_stand_alone_node_to_network(self):
        """add stand-alone nodes to the network and give weight=1000"""
        stand_alone_netlocs, popular_stand_alone_netlocs = self.find_stand_alone_nodes()

        """add popular stand-alones to the network """
        standalone_rows = [[u,u,1000] for u in popular_stand_alone_netlocs]
        standalone_df = pd.DataFrame(standalone_rows, columns=['source','target','weight'])
        self.df_network = self.df_network.append(standalone_df, ignore_index=True)

        """remove non-popular standalones from node list"""
        non_popular_standalones = [np for np in stand_alone_netlocs if np not in popular_stand_alone_netlocs]
        non_popular_filter = self.df_netlocs['url_netloc_clean'].isin(non_popular_standalones)
        self.df_netlocs = self.df_netlocs[~non_popular_filter]

    def save_network(self):

        save_dataframe(self.df_netlocs, self.netloc_output_file_name)
        save_dataframe(self.df_network, self.network_output_file_name)
        save_dataframe(self.df_netlocs_origin, self.netloc_origin_output_file_name)
