# coding=utf-8
# Copyright 2019 The MONPA team.
#
# CC BY-NC-SA 4.0 licence

"""Run BERT for MONPA."""

import argparse
import logging
import unicodedata
import torch

from monpa.modeling import BertConfig, BertForMONPA

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s', \
                    datefmt = '%m/%d/%Y %H:%M:%S', \
                    level = logging.INFO)
logger = logging.getLogger(__name__)

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
    conll_formatted = ''
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
    assert len(segmented_words) == len(pos_tags), \
           "lengths {} (words) and {} (pos tags) mismatch".format( \
                 (segmented_words), (pos_tags))
    for w,p in zip(segmented_words, pos_tags):
        conll_formatted += u"{}\t{}\n".format(w, p)
    return conll_formatted, segmented_words, pos_tags

def add_all_arguments(parser_object):
    import os
    path_monpa_package = os.path.dirname(os.path.abspath(__file__))
    path_bert_config_file = path_monpa_package + '/bert_configs/bert_config_monpa.json'
    path_vocab_file = path_monpa_package + '/bert_configs/vocab_monpa.vocab'
    path_output_vocab_file = path_monpa_package + '/bert_configs/pos.tgt.dict'
    path_model = path_monpa_package + '/model/model-511.pt'

    parser_object.add_argument("--bert_config_file", default=path_bert_config_file, type=str,
                        help="The config json file corresponding to the pre-trained BERT model. "
                             "This specifies the model architecture.")
    parser_object.add_argument("--vocab_file", default=path_vocab_file, type=str,
                        help="The vocabulary file that the BERT model was trained on.")
    parser_object.add_argument("--output_vocab_file", default=path_output_vocab_file, type=str,
                        help="The vocabulary file of output tags.")
    parser_object.add_argument("--model", default=path_model, type=str,
                        help="Initial checkpoint (usually from a pre-trained BERT model).")
    parser_object.add_argument("--do_lower_case", default=False, action='store_true',
                        help="Whether to lower case the input text. Should be True for uncased "
                             "models and False for cased models.")
    parser_object.add_argument("--max_seq_length", default=128, type=int,
                        help="The maximum total input sequence length after WordPiece tokenization. Sequences "
                             "longer than this will be truncated, and sequences shorter than this will be padded.")
    parser_object.add_argument("--batch_size", default=4, type=int,
                        help="Batch size.")
    parser_object.add_argument("--less_logging", default=False, action='store_true',
                        help="If true, print less logs. ")
    parser_object.add_argument("--input_file", type=str,
                        help="If set, read input from file instead of console.")
    parser_object.add_argument("--output_file", type=str,
                        help="If set, output to file instead of console.")
    parser_object.add_argument("--only_words", default=False, action='store_true',
                        help="If set, output only segmented words (no POS tags).")
    args = parser_object.parse_args()
    print(args)
    return args

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
                iid_to_tag = out_vocab[iid]
                if iid_to_tag == "[SEP]": break
                tags.append(iid_to_tag)
            output_tags.append(tags)
    return output_tags

def decode_stream(model, args, in_vocab, out_vocab):
    while True:
        try:
            sentence = input()
        except EOFError:
            return
        sentence = _strip_control_invalid_chars(sentence.strip())
        if len(sentence) < 1:
            return
        model_out = query_model(model, [sentence], args, in_vocab, out_vocab)
        model_out = model_out[0]
        conll_formatted, segmented_words, pos_tags = to_CoNLL_format(sentence, model_out)
        out_str = conll_formatted
        if args.only_words:
            out_str = ' '.join(segmented_words)
        print(out_str)

def decode_file(model, args, in_vocab, out_vocab):
    has_tqdm = False
    try:
        from tqdm import tqdm
        has_tqdm =True
    except:
        pass

    with open(args.input_file, encoding="utf-8") as in_f, open(args.output_file, 'w', encoding="utf-8") as out_f:
        lines = in_f.readlines()
        lines = [l.strip() for l in lines]
        lines = [_strip_control_invalid_chars(l) for l in lines]
        num_lines = len(lines)
        batch_size = args.batch_size
        num_batches = int((num_lines - 1) // batch_size) + 1
        batch_i = -1
        # results = []
        if has_tqdm:
            progress_bar = tqdm(total=num_batches)
        while True:
            batch_i += 1
            if has_tqdm:
                progress_bar.update(1)
            if batch_i * batch_size > num_lines:
                break
            batch_data = lines[batch_i * batch_size: (batch_i + 1) * batch_size]
            batch_out = query_model(model, batch_data, args, in_vocab, out_vocab)
            # results.append(batch_out)
            for bo_i, bo in enumerate(batch_out):
                conll_formatted, segmented_words, pos_tags = to_CoNLL_format(batch_data[bo_i], bo) # 0 is conll, 1 is words, 2 is pos tags
                out_str = ' '.join(conll_formatted)
                if args.only_words:
                    out_str = ' '.join(segmented_words)
                out_f.write(out_str)
                out_f.write('\n')
                out_f.flush()
    if has_tqdm:
        progress_bar.close()
    return

def main():
    parser = argparse.ArgumentParser()
    args = add_all_arguments(parser)
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

    if (args.input_file is not None) and (args.output_file is not None):
        decode_file(model, args, in_vocab, id_to_pos)
    else:
        decode_stream(model, args, in_vocab, id_to_pos)

if __name__ == "__main__":
    main()
