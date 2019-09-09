# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from termcolor import cprint
import tensorflow
from .aes import AES
from scaaml.utils import hex_display, hex_display_recovered_key
from scaaml.aes.combined_data import shard_to_dict
from tqdm import tqdm


def pred2byte(attack_point, pt, prediction_index):
    """Recover the byte value

    Args:
        attack_point (str): attack point target
        pt (int): Plain text value
        prediction_index (int): prediction index

    Raises:
        ValueError: if attack point is unknown

    Returns:
        int: byte value
    """

    if attack_point == 'add_round_key_out':
        byte_idx = prediction_index ^ pt
    elif attack_point == 'sub_bytes_in':
        byte_idx = prediction_index ^ pt
    elif attack_point == 'sub_bytes_out':
        byte_idx = AES.rsbox[prediction_index] ^ pt
    elif attack_point == 'key':
        return prediction_index
    else:
        raise ValueError('target point not implemented')
    return byte_idx


def prediction_to_byte_array(attack_point, pt, predictions):
    """Maps model predictions to byte predictions.

    Args:
        predictions (np.float): Array of predicted probabilities. 1D.
        pt (int): Plaintext.
        attack_point (str): The attack point being targeted.

    Returns:
        np.array (256,): Byte predictions.
    """
    byte_probabilities = np.zeros(256)

    for pred_idx, pred_value in enumerate(predictions):
        byte_idx = pred2byte(attack_point, pt, pred_idx)
        byte_probabilities[byte_idx] = pred_value

    return byte_probabilities


def check_byte_recovery(shard, byte_idx=0, attack_point='key', debug=1):
    "check if recovery code work "

    if debug:
        cprint('\nRecovery using target point %s:' % (attack_point), 'magenta')
    if debug:
        cprint("|-Key info:", 'magenta')

    key = shard.key[0]
    if debug:
        hex_display(key, prefix="key:\t\t", color='white')

    # plaintext
    pt = shard.pt[0]
    if debug:
        hex_display(pt, prefix="pt:\t\t", color='white')

    # ciphertext
    ct = shard.ct[0]
    if debug:
        hex_display(ct, prefix="ct:\t\t", color='yellow')

    # AES forward
    aes = AES()
    computed_ct = aes.encrypt(pt, key, 16)
    if debug:
        hex_display(computed_ct, prefix="computed_ct:\t", color='yellow')

    if attack_point == 'sub_bytes_in':
        true_intermediate = aes.intermediates['sbox_in'][0][byte_idx]
    elif attack_point == 'sub_bytes_out':
        true_intermediate = aes.intermediates['sbox_out'][0][byte_idx]
    else:
        true_intermediate = key[byte_idx]

    true_label = shard.y[0]

    guess_byte = pred2byte(attack_point, pt[byte_idx], true_label)

    if debug:
        print('|-Plain text:%s' % hex(pt[byte_idx]))
        print("|-Prediction: %s - expected: %s" %
              (hex(true_label), hex(true_intermediate)))
        print("|-Recovered Byte: %s" % (hex(guess_byte)))

        print("|-True Byte:%s" % (hex(key[byte_idx])))
    return int(guess_byte), int(key[byte_idx])


def compute_rank(byte_probabilities, real_byte):
    """Given predicted probabilities for a single example, compute the rank of
    the correct byte, within the predictions."""

    sorted_results = np.argsort(-byte_probabilities)
    for i in range(256):
        if sorted_results[i] == real_byte:
            return i
    raise ValueError("Invalid byte value: ", real_byte)


def compute_metrics_for_predictions(predicted,
                                    y_arr,
                                    pt_arr,
                                    attack_point="key",
                                    byte_idx=0,
                                    probability_accumulation='log10'):

    # Accumulated byte probabilities across traces.
    byte_probabilities = np.zeros(256)

    confusion_matrix = np.zeros([256, 256])
    ranks = []

    # Accumulate predictions to infer the most likely byte.
    for idx, prediction in enumerate(predicted):

        pt = pt_arr[idx][byte_idx]

        real_byte = pred2byte(attack_point, pt, y_arr[idx])

        trace_predictions = prediction_to_byte_array(attack_point, pt,
                                                     prediction)
        for proba_idx, probability in enumerate(trace_predictions):
            if probability_accumulation == 'log10':
                byte_probabilities[proba_idx] += np.log10(probability + 1e-22)
            else:
                byte_probabilities[proba_idx] += probability

        guess_byte = np.argmax(byte_probabilities)

        confusion_matrix[real_byte][guess_byte] += 1

        ranks.append(compute_rank(byte_probabilities, real_byte))

    return ranks, confusion_matrix


def process_batch(predict_fn,
                  data,
                  start_idx,
                  end_idx,
                  attack_point="key",
                  byte_idx=0,
                  probability_accumulation='log10'):

    x = data.x[start_idx:end_idx]
    y = data.y[start_idx:end_idx]
    pt = data.pt[start_idx:end_idx]
    preds = predict_fn(x)

    return compute_metrics_for_predictions(
        preds,
        y,
        pt,
        attack_point=attack_point,
        byte_idx=byte_idx,
        probability_accumulation=probability_accumulation)


def create_rank_table(ranks):
    top20 = 0
    top10 = 0
    top5 = 0
    top1 = 0

    for rank in ranks:
        if rank < 20:
            top20 += 1
        if rank < 10:
            top10 += 1
        if rank < 5:
            top5 += 1
        if rank == 0:
            top1 += 1

    results = [['num keys attacked', len(ranks)],
               ['mean_rank', float(np.mean(ranks))],
               ['max_rank', float(np.max(ranks))],
               ['median_rank', float(np.median(ranks))],
               ['min_rank', float(np.min(ranks))], ["top1", int(top1)],
               ["top5", int(top5)], ["top10", int(top10)],
               ["top20", int(top20)]]

    header = ["Metric", "Value"]
    return results, header


def side_channel_attack(model,
                        data,
                        attack_point="key",
                        byte_idx=0,
                        predict_fn=None,
                        probability_accumulation='log10'):
    ranks = []
    rank_histories = []
    confusions = []
    summed_confusion = np.zeros([256, 256])

    if not predict_fn:
        predict_fn = lambda x: model.predict(x)

    batch_start = 0
    last_key = data.key[0]
    key = data.key[0]

    # Data - currently in the order it was pulled from shards.

    idx = 0
    for idx in range(1, len(data.x)):
        key = data.key[idx]

        if not np.array_equal(data.key[idx], last_key):
            rank_history, confusion = process_batch(
                predict_fn,
                data,
                batch_start,
                idx,
                attack_point=attack_point,
                byte_idx=byte_idx,
                probability_accumulation=probability_accumulation)
            ranks.append(rank_history[-1])
            rank_histories.append(rank_history)
            confusions.append(confusion)
            summed_confusion = summed_confusion + confusion
            batch_start = idx
            last_key = key

    if idx != batch_start:
        rank_history, confusion = process_batch(
            predict_fn,
            data,
            batch_start,
            idx + 1,
            attack_point=attack_point,
            byte_idx=byte_idx,
            probability_accumulation=probability_accumulation)
        ranks.append(rank_history[-1])
        rank_histories.append(rank_history)
        confusions.append(confusion)
        summed_confusion = summed_confusion + confusion
        batch_start = idx
        last_key = key

    return ranks, rank_histories, confusions, summed_confusion
