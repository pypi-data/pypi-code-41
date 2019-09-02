# coding=utf-8
# Copyright 2019 The MONPA team.
# CC BY-NC-SA 4.0 licence
"""Run BERT for MONPA."""


from argparse import Namespace
import argparse
import logging
import unicodedata
import torch
import os
import os.path as path
import sys
import time

from monpa.modeling import BertConfig, BertForMONPA

__version__ = "The installed MONPA version: 0.2.6.0"

print("+---------------------------------------------------------------------+")
print("  Welcome to MONPA: Multi-Objective NER POS Annotator for Chinese")
# print("version: ", __version__)
# print("Date: 2019/08/30")
# print("for debug purposes, please ignore it")
# print("current path:", os.path.abspath('.'))
# print("__file__ path:", os.path.abspath(__file__))
# print("monpa package path:", os.path.dirname(os.path.abspath(__file__)))
print("+---------------------------------------------------------------------+")

path_monpa_package = os.path.dirname(os.path.abspath(__file__))# os.path.abspath(__file__).strip("__init__.py")
path_bert_config_file = path_monpa_package + '/bert_configs/bert_config_monpa.json'
path_output_vocab_file = path_monpa_package + '/bert_configs/pos.tgt.dict'
path_vocab_file = path_monpa_package + '/bert_configs/vocab_monpa.vocab'
path_model = path_monpa_package + '/model/model-830.pt'
download_model_url = "http://nlp.tmu.edu.tw/monpa_model/model-830.pt"

if os.path.exists(path_model):
    print("Good, we can find the model file.")
else:
    import requests
    print("首次使用 monpa 將會直接下載 model-830.pt 檔，約 200MB，並儲存於 monpa package 資料夾，下次就不需再下載。")
    print("For first-time users, we will automatically download the model file (around 200MB).")
    # r = requests.get(download_model_url)
    # with open(path_model, 'wb') as f:
    #    f.write(r.content)
    with open(path_model, 'wb') as f:
        r = requests.get(download_model_url, stream=True)
        total_length = int(r.headers.get('content-length'))
        print("Total  file  size:", total_length, "KB")
        dl = 0
        percent = 0.1
        if total_length is None: # no content length header
            f.write(r.content)
        else:
            for chunk in r.iter_content(10240):
                dl += len(chunk)
                f.write(chunk)
                #print("Downloaded volume:", dl, "KB", end="")
                done = dl / total_length
                if done >= percent: 
                    print("#", end="")
                    percent += 0.1
    print("已完成 monpa model v830 下載，歡迎使用。Model v830 has been downloaded.")

args = Namespace(batch_size=4, \
                 bert_config_file=path_bert_config_file, \
                 do_lower_case=False, \
                 input_file=None, \
                 less_logging=False, \
                 max_seq_length=128, \
                 model=path_model, \
                 only_words=False, \
                 output_file=None, \
                 output_vocab_file=path_output_vocab_file, \
                 vocab_file=path_vocab_file)

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s', \
                    datefmt = '%m/%d/%Y %H:%M:%S', \
                    level = logging.INFO)
logger = logging.getLogger(__name__)

assert bool(args.input_file) == bool(args.output_file), \
           "input file and output file must be specified together."
if args.less_logging:
        logger.setLevel(logging.WARNING)
args.__dict__['device'] = torch.device("cpu")
logger.info("running on device %s", args.device)

bert_config = BertConfig.from_json_file(args.bert_config_file)

if args.max_seq_length > bert_config.max_position_embeddings:
    raise ValueError(
            "Cannot use sequence length %d because the BERT model "
            "was only trained up to sequence length %d" %
            (args.max_seq_length, bert_config.max_position_embeddings))

in_vocab = dict()
with open(args.vocab_file, encoding="utf-8") as in_v_file:
    for w in in_v_file.readlines():
        w = w.strip()
        if len(w) < 1: continue
        in_vocab[w] = len(in_vocab)

out_vocab = dict()
with open(args.output_vocab_file, encoding="utf-8") as out_v_file:
    for w in out_v_file.readlines():
        w = w.strip()
        if len(w) < 1: continue
        out_vocab[w] = len(out_vocab)

id_to_pos = dict([(v, k) for (k, v) in out_vocab.items()])

bert_config.pos_tag_size = len(out_vocab)
bert_config.tag_id_to_name = id_to_pos

model = BertForMONPA(bert_config)

checkpoint_dict = torch.load(args.model, map_location='cpu')
model_params = model.state_dict()
model_params.update(checkpoint_dict)
model.load_state_dict(model_params)
model.eval()


def convert_tokens_to_ids(vocab, tokens):
    """Converts a sequence of tokens into ids using the vocab."""
    ids = []
    has_unk = vocab.get("[UNK]")
    for t in tokens:
        try:
            ids.append(vocab[t])
        except:
            if has_unk is not None:
                ids.append(has_unk)
            else:
                print("Does not allow UNK")
                print(t)
                print(tokens)
                exit()
    return ids

def _strip_control_invalid_chars(input_str):
    return_string = ""
    for cp in input_str:
        if cp == '\t' or cp == '\n' or cp == '\r': continue
        cp_code = ord(cp)
        if cp_code == 0 or cp_code == 0xfffd: continue
        cat = unicodedata.category(cp)
        if cat.startswith("C"): continue
        return_string += cp
    return return_string

def to_CoNLL_format(org_input, predicted_pos):
    conll_formatted = []
    segmented_words = []
    pos_tags = []
    # print (len(org_input))
    # print (len(predicted_pos))
    temp_word = ''
    for pos_id, pos_name in enumerate(predicted_pos):
        if pos_id >= len(org_input):
            break
        split_pos_names = pos_name.split('-')
        if len(split_pos_names) == 3:
            bound, _, detailed_pos = split_pos_names
        elif len(split_pos_names) == 2:
            bound, detailed_pos = split_pos_names
        else:
            break
        bound = bound.lower()
        if bound == 's':
            pos_tags.append(detailed_pos)
            segmented_words.append(org_input[pos_id])
            continue
        temp_word += org_input[pos_id]
        if bound == 'b':
            pos_tags.append(detailed_pos)
        if bound == 'e':
            segmented_words.append(temp_word)
            temp_word = ''
    if len(segmented_words) < len(pos_tags):
        segmented_words.append(temp_word) #without "e", force to append. This is an incomplete sentence.
        temp_word = ''
    assert len(segmented_words) == len(pos_tags), \
           "lengths {} (words) and {} (pos tags) mismatch".format( \
                 (segmented_words), (pos_tags))
    for w,p in zip(segmented_words, pos_tags):
        conll_formatted.append([w,p])
        # conll_formatted += u"{} {}\n".format(w, p)
        # conll_formatted += u"{}\t{}\n".format(w, p)
    return conll_formatted, segmented_words, pos_tags

def pad_inputs(input_ids, input_mask, segment_ids):
    max_len = max([len(ii) for ii in input_ids])
    padded_input_ids, padded_input_mask, padded_segment_ids = [], [], []
    for i in range(len(input_ids)):
        padded_input_ids.append(input_ids[i] + ([0] * (max_len - len(input_ids[i]))))
        padded_input_mask.append(input_mask[i] + ([0] * (max_len - len(input_mask[i]))))
        padded_segment_ids.append(segment_ids[i] + ([0] * (max_len - len(segment_ids[i]))))

    return padded_input_ids, padded_input_mask, padded_segment_ids

def query_model(model, input_text_tokens, args, in_vocab, out_vocab):
    input_text_tokens = [_strip_control_invalid_chars(ts) for ts in input_text_tokens]
    input_text_tokens = [list(ts[:args.max_seq_length]) + ["[SEP]"] for ts in input_text_tokens]
    segment_ids = [[0] * len(ts) for ts in input_text_tokens]
    input_mask = [[1] * len(ts) for ts in input_text_tokens]
    # word to ID
    input_ids = [convert_tokens_to_ids(in_vocab, ts) for ts in input_text_tokens]

    if len(input_ids) > 1: # batch length > 1, need padding
        input_ids, input_mask, segment_ids = pad_inputs(input_ids, input_mask, segment_ids)

    input_ids = torch.tensor(input_ids, dtype=torch.long)
    input_mask = torch.tensor(input_mask, dtype=torch.long)
    segment_ids = torch.tensor(segment_ids, dtype=torch.long)
    device = args.device
    input_ids = input_ids.to(device)
    input_mask = input_mask.to(device)
    segment_ids = segment_ids.to(device)

    output_tags = []

    with torch.no_grad():
        all_ids = model(input_ids, segment_ids, input_mask)
        for ids in all_ids:
            tags = []
            for iid in ids:
                iid_to_tag = id_to_pos[iid] # out_vocab[iid]
                if iid_to_tag == "[SEP]": break
                tags.append(iid_to_tag)
            output_tags.append(tags)
    return output_tags

# load user dictionary function
userdict = []
def load_userdict(pathtofile):
    global userdict
    # empty previous userdict
    userdict = []
    for input_item in open(pathtofile, 'r', encoding="utf-8").read().split("\n"):
        userdict.append(input_item.split(" "))

# Yields all the positions of the pattern p in the string s.
def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)


def cut_wo_userdict(text):
    # while True:
    try:
        sentence = text # input()
    except EOFError:
        return
    sentence = _strip_control_invalid_chars(sentence.strip())
    if len(sentence) < 1:
        return
    model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
    model_out = model_out[0]
    conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
    # out_str = conll_formatted
    out_str = segmented_words
    # if args.only_words:
    #    out_str = ' '.join(segmented_words)
    # print(out_str)
    return(out_str)

# segment within user defined dict and return terms without POS
def cut_w_userdict(text):
    from operator import itemgetter, attrgetter
    # find user defined dict terms' position within sentence or not
    userdict_in_sentence = []
    text_temp = text.encode().decode()
    for term_dict in userdict:
        for term_index in findall(term_dict[0], text_temp):
            text_temp = text_temp.replace(term_dict[0], "＃"*len(term_dict[0]))
            if term_dict[0] == '':break
            userdict_in_sentence.append([term_index, term_dict[0]])

    j = 0
    sentence_list = []
    userdict_in_sentence_sorted = sorted(userdict_in_sentence, key=itemgetter(0))
    #print(userdict_in_sentence_sorted)
    for term in userdict_in_sentence_sorted:
        org_inputs = []
        if term[0] == j:
            # print(term)
            sentence_list.append(term[1])
            j = j+ len(term[1])
            if len(userdict_in_sentence_sorted) - (userdict_in_sentence_sorted.index(term)+1) == 0:
                sentence = text[j:]
                sentence = _strip_control_invalid_chars(sentence.strip())
                model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
                model_out = model_out[0]
                conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
                out_str = segmented_words
                sentence_list.extend(out_str)
                break
        else:
            sentence = text[j: term[0]]
            sentence = _strip_control_invalid_chars(sentence.strip())
            model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
            model_out = model_out[0]
            conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
            out_str = segmented_words
            sentence_list.extend(out_str)
            sentence_list.append(term[1])
            j = term[0] + len(term[1])
            if len(userdict_in_sentence_sorted) - (userdict_in_sentence_sorted.index(term)+1) == 0:
                sentence = text[j:]
                sentence = _strip_control_invalid_chars(sentence.strip())
                model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
                model_out = model_out[0]
                conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
                out_str = segmented_words
                sentence_list.extend(out_str)
                break
    return sentence_list


def pseg_wo_userdict(text):
    # while True:
    try:
        sentence = text # input()
    except EOFError:
        return
    sentence = _strip_control_invalid_chars(sentence.strip())
    if len(sentence) < 1:
        return
    model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
    model_out = model_out[0]
    conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
    out_str = conll_formatted # .split("\n")[:-1]
    return(out_str)

def pseg_w_userdict(text):
    from operator import itemgetter, attrgetter
    # find user defined dict terms' position within sentence or not
    userdict_in_sentence = []
    text_temp = text.encode().decode()
    for term_dict in userdict:
        for term_index in findall(term_dict[0], text_temp):
            text_temp = text_temp.replace(term_dict[0], "＃"*len(term_dict[0]))
            if term_dict[0] == '':break
            userdict_in_sentence.append([term_index, term_dict[0], term_dict[2]])

    j = 0
    sentence_list = []
    userdict_in_sentence_sorted = sorted(userdict_in_sentence, key=itemgetter(0))
    # print(userdict_in_sentence_sorted)
    for term in userdict_in_sentence_sorted:
        org_inputs = []
        if term[0] == j:
            # print(term)
            sentence_list.append([term[1], term[2]])
            j = j+ len(term[1])
            if len(userdict_in_sentence_sorted) - (userdict_in_sentence_sorted.index(term)+1) == 0:
                sentence = text[j:]
                sentence = _strip_control_invalid_chars(sentence.strip())
                model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
                model_out = model_out[0]
                conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
                out_str = conll_formatted # .split("\n")[:-1]
                sentence_list.extend(out_str)
                break
        else:
            sentence = text[j: term[0]]
            sentence = _strip_control_invalid_chars(sentence.strip())
            model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
            model_out = model_out[0]
            conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
            out_str = conll_formatted # .split("\n")[:-1]
            sentence_list.extend(out_str)
            sentence_list.append([term[1], term[2]])
            j = term[0] + len(term[1])
            if len(userdict_in_sentence_sorted) - (userdict_in_sentence_sorted.index(term)+1) == 0:
                sentence = text[j:]
                sentence = _strip_control_invalid_chars(sentence.strip())
                model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
                model_out = model_out[0]
                conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
                out_str = conll_formatted # .split("\n")[:-1]
                sentence_list.extend(out_str)
                break
    return sentence_list

# no using user dict, return words only
def cut(text):
    if userdict == []:
        return cut_wo_userdict(text)
    else:
        if any(x[0] in text for x in userdict):
            return cut_w_userdict(text)
        else:
            return cut_wo_userdict(text)

def pseg(text):
    if userdict == []:
        return pseg_wo_userdict(text)
    else:
        if any(x[0] in text for x in userdict):
            return pseg_w_userdict(text)
        else:
            return pseg_wo_userdict(text)

#if __name__ == "__main__":
#    main()
