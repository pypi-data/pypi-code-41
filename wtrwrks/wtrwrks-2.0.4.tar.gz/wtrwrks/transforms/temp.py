"""
add_tensors : dict of tensors
  Any additional tensors to add into the dataset object.

batch_size : int
  The number of example to include in a single batch.

cat_val_to_index : dict
  The mapping from category value to index number.

cols : list of strs
  The column names of the array or dataframe to be transformed.

data : np.ndarray
  The numpy array to transform.

data : np.array or pd.DataFrame
  The entire dataset in the form of a numpy array or a pandas DataFrame. Should have the same columns as the arrays that will be fed to the pour method.

data_iter : iterator of np.array or pd.DataFrame
  The entire dataset in the form of an iterator of numpy array or a pandas DataFrame. Needed if the dataset is too large to fit in memory. Should have the same columns as the arrays that will be fed to the pour method. Can only use if 'data' is not being used

dataset_iter : tf.data.Iterator
  The dataset object to feed into tensorflow training pipelines.

drop_features : list of strs
  The features to drop when reading from the tfrecords. Defaults to None. Can only use this or keep_features not both.

dtype : numpy dtype
  The data type the transformed data should have. Defaults to np.float64.

examples : list of dicts of features
  The example dictionaries which contain tf.train.Features.

from_file : str
  The path to the saved file to recreate the transform object that was saved to disk.

file_name : str
  The name of the tfrecord file to write to. An extra '_<num>' will be added to the name.

file_name_pattern : string
  The file name pattern of the tfrecord files. Supports '*', etc.

file_num_offset : int
  A number that controls what number will be appended to the file name (so that files aren't overwritten.)

filters : dict of functions
  Any pre preprocessing filters to put on the dataset. The keys are the filter names, the values are the filter themselves

funnel_dicts : list of dicts(
  keys - Slot objects or Placeholder objects. The 'funnels' (i.e. unconnected slots) of the waterwork.
  values - valid input data types
)
  The inputs to the waterwork's full pour functions. There is exactly one funnel_dict for every process.


index_to_cat_val : list
  The mapping from index number to category value.

index_to_word : list
  The mapping from index number to word.

index_to_word_maps : dic of lists
  A dictionary which maps a language to a list. Each list is a mapping from index number to word.

input_dtype: numpy dtype
  The datatype of the original inputted array.

input_shape: list of ints
  The shape of the original inputted array.

keep_features : list of strs
  The features to keep after reading in from the tfrecords. Defaults to all of them.

name : str
  The name of the transform.

norm_axis : 0, 1, or None
  In the case that 'norm_mode' has a non None value, what axis should be used for the normalization. None implies both 0 and 1.

norm_mode : "mean_std" or None
  How to normalize the data. Subtracting out the mean and dividing by the standard deviation or leaving as is.

num_examples : int
  The number of rows that have passed through the calc_global_values function.

num_steps : int
  Number of steps to run in the dataset before terminating. Cannot use when num_epochs is defined

num_threads : int
  The number of io threads to use. Defaults to 1, should probably not be more than 3.

mean : numpy array
  The stored mean values to be used to normalize data.

prefix : str
  Any additional prefix string/dictionary keys start with. Defaults to no additional prefix.

recreate : bool
  Whether or not to force the transform to create a new waterwork.

save_dict : dict
  The dictionary to recreate the transform object.

schema_dict : dict
  Dictionary where the keys are the field names and the values are the SQL data types.

shuffle_buffer_size : int
  How many examples to shuffle together.

skip_fails : bool
  Whether or not to skip any write failures without error. Defaults to false.

skip_keys : list of strs
  Any taps that should not be written to examples.

std : numpy array
  The stored standar deviation values to be used to normalize data.

tap_dict : dict (or iterator of dicts)
  The dictionary of transformed outputs as well as any additional information needed to completely reconstruct the original data. Returns an iterator of dicts if something is passed to 'data_iter' rather than the 'data' argument.

tap_dict: dict
  The dictionary all information needed to completely reconstruct the original data.

to_prefix : str or dict
  The string or dictionary to add to the prefix/self.name prefix to.

to_unprefix : str or dict
  The string or dictionary to strip the prefix/self.name  from.

var_lim : int or dict
  The maximum size of strings. If an int is passed then all VARCHAR fields have the same limit. If a dict is passed then each field gets it's own limit. Defaults to 255 for all string fields.

Waterwork
  The waterwork object that this transform creates.

word_detokenizer : func
  A function that takes in a list of words and outputs a string. Doesn't have to be an exact inverse to word_tokenizer but should be close otherwise a lot of large diff strings will have to be outputted in order to reproduce the original strings.

word_detokenizers : dict of funcs
  A dicitonary of which maps a language to a function. The functions take in a list of words and output a string. Doesn't have to be an exact inverse to word_tokenizer but should be close otherwise a lot of large diff strings will have to be outputted in order to reproduce the original strings.

word_to_index : dict
  The mapping from word to index number.

word_to_index_maps : dict of dict
  A dicitionary which maps a language to a another mapping. The mapping is from word to index number.

word_tokenizers : dict of funcs
  A dicitonary of which maps a language to a function. The functions take in a string and split it up into a list of words.

word_tokenizer : func
  A function that takes in a string and splits it up into a list of words.



"""
