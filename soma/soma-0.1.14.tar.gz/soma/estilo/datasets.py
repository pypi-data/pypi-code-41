"""
    This module comprises the Datasets class, used for creating trainable datasets,
    separated into train/test subsets.

    For this module to work, 3 environment variables need to be set:
    
    SALES_DATASET_PATH -> Path for saving/loading the dataset.
    ANIMALE_SALES_PATH -> Path of the sales data in pickle format. (REQUIRED)
    ANIMALE_TAGS_PATH -> Path of the tags data in pickle format.

    If the tags data is not found, it is queried from the databse.
    For that, additional environment variables need to be set regarding 
    credentials used for connecting to the database.
"""
from soma.estilo import modelling, utils
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import os


class Datasets:
    """
        Datasets class definition.

        This class encapsulates all necessary methods 
        to create (if needed) relevant datasets for further analyses.

        Attributes:
            train (:class:`numpy.ndarray`): The data subset used for training.
            test (:class:`numpy.ndarray`): The data subset used for testing.
            path (str):
            desc (str): Dataset problem description, either 'REG' for regression or 'CLF' for classification problems.
            label_columns (list(str)): A list containing the name of the columns that were label-encoded.
            dataset (:class:`pandas.DataFrame`): The raw dataset, before splitting into train/test data and encoding.
    """

    def __init__(self):
        """
            Initializes class attributes
        """
        self.train = None
        self.train_ = None
        self.test = None
        self.test_ = None
        self.path = None
        self.desc = None
        self.label_columns = None
        self.dataset = None

    def load_sales(
        self,
        encoder=None,
        train_collections=["VER18", "INV18"],
        test_collections=["VER19"],
        clf=False,
        cols=[
            "qtde",
            "linha",
            "grupo",
            "preco",
            "disc",
            "category",
            "apparel",
            "productpattern",
            "bodygarment",
            "giro",
        ],
    ):
        """
            Loads the sales dataset using product tags.

            Args:
                encoder (:class:`sklearn.base.BaseEstimator`): A Categorical encoder with at least a fit,
                fit_transform and transform methods.
                train_collections (list(str)): List of collections to be used as training data.
                test_collections (list(str)): List of collections to be used as testing data.
                clf (bool): Flag indicating if the dataset is going to be used in a classification or regression problem
        """

        try:
            with open(os.environ.get("SALES_DATASET_PATH"), "rb") as f:
                dataset = pd.read_pickle(f)
                self.dataset = dataset
        except:
            dataset = self.create_sales()

        with open(os.environ.get("SALES_DATASET_PATH"), "wb") as f:
            pickle.dump(dataset, f)

        label_mask = dataset.dtypes.to_numpy() == "O"
        self.label_columns = dataset.columns[label_mask]

        train_mask = dataset["colecao"].isin(train_collections)
        test_mask = dataset["colecao"].isin(test_collections)

        if clf:
            top_giro = (
                dataset[train_mask]["giro"].mean()
                + dataset[train_mask]["giro"].std() * 0.5
            )
            bot_giro = (
                dataset[train_mask]["giro"].mean()
                - dataset[train_mask]["giro"].std() * 0.5
            )
            dataset["giro"] = dataset["giro"].apply(
                lambda x: 1 * (x > top_giro) + 2 * (x < bot_giro)
            )
            self.type = "CLF"
        else:
            self.type = "REG"

        dataset = dataset[cols]

        if encoder:
            encoder = encoder(cols=list(set(self.label_columns) & set(cols)))
            dataset = encoder.fit_transform(dataset)
            self.desc = "Encoded_dataset"
        else:
            self.desc = "Non_Encoded_dataset"

        dataset_train = dataset[train_mask][:]
        dataset_test = dataset[test_mask][:]

        self.train = (dataset_train.to_numpy()[:, :-1], dataset_train.to_numpy()[:, -1])
        self.test = (dataset_test.to_numpy()[:, :-1], dataset_test.to_numpy()[:, -1])

        self.train_ = (
            dataset_train.to_numpy()[:, :-1],
            dataset_train.to_numpy()[:, -1],
        )
        self.test_ = (dataset_test.to_numpy()[:, :-1], dataset_test.to_numpy()[:, -1])

        return self

    def split_df(tags):
        """
            Correctly structures the tags information into a DataFrame.

            Args:
                tags(:class:`pandas.DataFrame`): The tags DataFrame.
        """
        type_df = str(tags.columns[1])
        tags = tags.groupby("%s" % tags.columns[0]).apply(
            lambda x: x["%s" % tags.columns[1]].str.cat(sep=",")
        )
        tags = pd.DataFrame(tags).reset_index()
        tags.columns = ["id", "nome"]
        tags = tags.set_index("id")
        split_tags = tags["nome"].str.split(",", expand=True)
        split_tags = split_tags.set_index(tags.index.values)

        if type_df == "desc_Fashion_Attributes":
            replace_dict = {
                "Garment": "garment",
                "Body": "body",
                "Length": "length",
                "Type": "type",
                "Color": "color",
                "heelHeight": "heelheight",
                "SkirtShape": "skirtshape",
                "Shape": "shape",
                "Style": "style",
                "productPattern": "productpattern",
            }

            split_tags.replace(replace_dict, regex=True, inplace=True)
            # Organizes the tags in major groups.
            fixed_tags = utils.reorganize_tags(split_tags).reset_index()
            fixed_tags.rename(
                columns={fixed_tags.columns[0]: "id_produto_cor"}, inplace=True
            )
            return fixed_tags
        split_tags.reset_index(inplace=True)
        split_tags.rename(
            columns={split_tags.columns[0]: "id_produto_cor"}, inplace=True
        )
        if type_df == "desc_Fashion_Occasion":
            split_tags.rename(
                columns={
                    split_tags.columns[1]: "Occasion_1",
                    split_tags.columns[2]: "Occasion_2",
                    split_tags.columns[3]: "Occasion_3",
                },
                inplace=True,
            )
        if type_df == "desc_Fashion_Style":
            split_tags.rename(
                columns={
                    split_tags.columns[1]: "Style_1",
                    split_tags.columns[2]: "Style_2",
                    split_tags.columns[3]: "Style_3",
                    split_tags.columns[4]: "Style_4",
                    split_tags.columns[5]: "Style_5",
                },
                inplace=True,
            )
        return split_tags

    def create_sales(self):
        """
            Creates the sales dataset using product tags.
        """

        # Trying to load existing tags, if it doesn't exist,
        # load from database (NEEDS environment variables).
        try:
            fixed_tags = pd.read_pickle(os.environ.get("ANIMALE_TAGS_PATH"))
        except:
            with open(os.environ.get("TAGS_QUERY_PATH"), "r") as f:
                query = f.read()
            q_l = query.split(sep=";")
            q_l.pop()
            df_list = []
            for q in q_l:
                df_list.append = utils.connect_and_query(q)
            tags = df_list[0]
            tag_occ = df_list[1]
            tag_stl = df_list[2]

            tag_occ = split_df(tag_occ)
            tag_stl = split_df(tag_stl)
            tags = split_df(tags)

            fixed_tags = pd.merge(tags, tag_stl, on="id_produto_cor")
            fixed_tags = pd.merge(fixed_tags, tag_occ, on="id_produto_cor")

            # Saves the organized tags for future use
            with open(os.environ.get("ANIMALE_TAGS_PATH"), "wb") as f:
                pickle.dump(fixed_tags, f)

        # Trying to load sales data, if it doesn't exist
        # throw an error.
        try:
            animale_df = pd.read_pickle(os.environ.get("ANIMALE_SALES_PATH"))
        except:
            print("File Doesn't exist")
            return 0

        # Dropping unnecessary products.
        animale_df = utils.clean_animale_dataset(animale_df)
        animale_df.rename(columns={"preco_varejo_original": "preco"}, inplace=True)
        animale_df.drop(
            animale_df.loc[animale_df["grupo"] == "SAPATOS"].index, inplace=True
        )
        animale_df.drop(
            animale_df.loc[animale_df["grupo"] == "SAPATILHA"].index, inplace=True
        )
        animale_df.drop(
            animale_df.loc[animale_df["grupo"] == "BOLSAS"].index, inplace=True
        )
        animale_df.drop(
            animale_df.loc[animale_df["grupo"] == "DIVERSOS"].index, inplace=True
        )
        animale_df.drop(
            animale_df.loc[animale_df["grupo"] == "CINTOS"].index, inplace=True
        )
        animale_df.drop(
            animale_df.loc[animale_df["grupo"] == "ACESSORIOS"].index, inplace=True
        )

        # Merging sales with tags.
        animale_df = animale_df.merge(fixed_tags, on="id_produto_cor")
        animale_df.reset_index(inplace=True, drop=True)

        # Grouping different TOPs.
        animale_df["grupo"].replace(r"^(TOP) (.*)", r"\1", regex=True, inplace=True)
        animale_df["grupo"].replace(r"^(OVERTOP)(.*)", r"\1", regex=True, inplace=True)

        # Merging garment columns.
        animale_df["bodygarment"] = (
            animale_df["lowerbodygarment"].fillna("")
            + animale_df["upperbodygarment"].fillna("")
            + animale_df["fullbodygarment"].fillna("")
        )

        # Merging length columns
        animale_df["bodylength"] = animale_df["upperbodylength"].fillna(
            ""
        ) + animale_df["lowerbodylength"].fillna("")

        animale_df.drop(
            columns=[
                "lowerbodygarment",
                "upperbodygarment",
                "fullbodygarment",
                "lowerbodylength",
                "upperbodylength",
            ],
            inplace=True,
        )

        # Dropping unnecessary columns
        animale_df.drop(
            [
                "bag",
                "clutch",
                "sneakers",
                "boots",
                "sandals",
                "sandaltype",
                "heeltype",
                "heelheight",
                "footwear",
                "shoe",
                "shoes",
                "shoetype",
                "toeshape",
                "toetype",
            ],
            axis=1,
            inplace=True,
        )

        # Adding product's intended entry date
        pcp_df = utils.get_pcp_dates(os.environ.get("PCP_QUERY_PATH"))
        animale_df = animale_df.merge(pcp_df, how="left", on="id_produto_cor")
        animale_df["min(entrega_final)"] = pd.to_datetime(animale_df["min(entrega_final)"])

        # Adding collection's dates
        col_df = utils.get_col_dates(os.environ.get("COL_QUERY_PATH"))
        animale_df = animale_df.merge(col_df, how="left", on="colecao")

        animale_df["delta_lancamento"] = (animale_df["lancamento"] - animale_df["minDate"]).dt.days
        animale_df["delta_fim"] = (animale_df["fim"] - animale_df["minDate"]).dt.days

        animale_df["delta_prog"] = (animale_df["min(entrega_final)"] - animale_df["minDate"]).dt.days
        # Saving the dataset pre-encoding.
        self.dataset = animale_df.copy()

        return animale_df

    def scale_input(self, scaler=StandardScaler()):
        """
            Scales the model's input using any scaler object.

            Args:
                scaler (): Any scaler (min-max, z-score, etc) with :func:`fit` and :func:`transform` methods.
        """
        X_train, Y_train = self.train_
        X_test, Y_test = self.test_

        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)

        self.train = (X_train, Y_train)
        self.test = (X_test, Y_test)
