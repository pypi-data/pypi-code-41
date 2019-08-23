# Copyright (c) 2018, Teriks
# All rights reserved.
#
# kovit is distributed under the following BSD 3-Clause License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


try:
    import ujson as json
except ImportError:
    import json

import math

from collections import OrderedDict

from ijson import ObjectBuilder

from kovit.bag import ProbabilityBag

try:
    from ijson.backends import yajl2_cffi as ijson
except ImportError as e:
    import ijson


def dump_json_small(chain, file, frequency_compress=True):
    codes = {}
    codes_list = []

    if frequency_compress:
        for code, v in enumerate(sorted(chain.build_frequency_dict().items(), key=lambda x: -x[1])):
            v = v[0]
            value = json.dumps(v)
            if code > 9 and (int(math.log10(code)) + 1) >= len(value):
                codes[v] = v
                codes_list.append(v)
                codes_list.append(v)
            else:
                codes[v] = code
                codes_list.append(code)
                codes_list.append(v)

        def gen_start(start):
            return codes[start]

        def gen_next_start(choices):
            for val, cnt in choices:
                yield tuple(codes[s] for s in val)
                yield cnt
    else:
        def gen_start(start):
            return start

        def gen_next_start(choices):
            for val, cnt in choices:
                yield val
                yield cnt

    def gen_chain():
        for start, bag in chain.items():
            yield gen_start(start)
            yield tuple(gen_next_start(bag.choices()))

    json.dump(OrderedDict((('codes', codes_list), ('chain', tuple(gen_chain())))), file)


def load_json_small(chain, file, merge=False):
    obj = json.load(file)

    c_iter = iter(obj['codes'])
    codes = dict(zip(c_iter, c_iter))

    c_list = iter(obj['chain'])

    if merge:
        if codes:
            for start, bag in zip(c_list, c_list):
                i_bag = iter(bag)
                for items, count in zip(i_bag, i_bag):
                    chain.add_to_bag(codes[start], tuple(codes[i] for i in items), count=count)
        else:
            for start, bag in zip(c_list, c_list):
                i_bag = iter(bag)
                for items, count in zip(i_bag, i_bag):
                    chain.add_to_bag(start, items, count=count)
    else:
        chain.clear()

        if codes:
            for start, bag in zip(c_list, c_list):
                i_bag = iter(bag)
                b = ProbabilityBag()
                for items, count in zip(i_bag, i_bag):
                    b.add(tuple(codes[i] for i in items), count=count)
                chain.set_bag(codes[start], b)
        else:
            for start, bag in zip(c_list, c_list):
                i_bag = iter(bag)
                b = ProbabilityBag()
                for items, count in zip(i_bag, i_bag):
                    b.add(tuple(items), count=count)
                chain.set_bag(start, b)


def dump_json_big(chain, file, frequency_compress=True):
    file.write('{"codes":[')

    if frequency_compress:
        codes = {}

        freq_dict = chain.build_frequency_dict().items()
        end_freqs = len(freq_dict) - 1

        for code, v in enumerate(sorted(freq_dict, key=lambda x: -x[1])):
            value = json.dumps(v[0])
            w_code = code

            if code > 9 and (int(math.log10(code)) + 1) >= len(value):
                codes[v[0]] = value
                w_code = value
            else:
                codes[v[0]] = code

            file.write('{},{}{}'.format(w_code, value, ',' if code != end_freqs else ''))

        def write_start(start):
            file.write('{},['.format(codes[start]))

        def write_next_start(next_start):
            file.write('[' + ','.join(str(codes[n]) for n in next_start) + ']')
    else:
        def write_start(start):
            file.write('{},['.format(json.dumps(start)))

        def write_next_start(next_start):
            file.write(json.dumps(next_start))

    file.write('],"chain":[')

    chain_end = len(chain) - 1

    for idx, v in enumerate(chain.items()):
        start, bag = v

        write_start(start)

        bag_end = bag.unique_count - 1

        for idx2, v2 in enumerate(bag.choices()):
            next_start, count = v2
            write_next_start(next_start)
            file.write(',{}{}'.format(count, ',' if idx2 != bag_end else ''))

        file.write('],' if idx != chain_end else ']')

    file.write(']}')


def load_json_big(chain, file, merge=False):
    if not merge:
        chain.clear()

    parser = ijson.parse(file)

    depth = 0

    builder = ObjectBuilder()

    codes = None

    building_bag_item = False

    start = None

    in_bag = False
    in_chain = False
    in_codes = False

    last_value = None
    last_key = None

    for prefix, event, value in parser:

        is_start = event.startswith('start_')
        is_end = event.startswith('end_')
        start_array = event == 'start_array'
        end_array = event == 'end_array'

        if is_start:
            depth += 1
        if is_end:
            depth -= 1
        if event == 'map_key':
            last_key = value
        if event == 'number' or event == 'string':
            last_value = value

        if not (in_codes or in_chain) and start_array and depth == 2:
            if last_key == 'codes':
                in_codes = True
                builder.event(event, value)
            elif last_key == 'chain':
                in_chain = True
        elif event == 'end_array' and depth == 1:
            if in_codes:
                liter = iter(builder.value)
                codes = dict(zip(liter, liter))
                builder.event(event, value)
                in_codes = False
            if in_chain:
                in_chain = False
        elif in_chain and start_array and depth == 3:
            in_bag = True
            start = last_value
        elif in_chain and end_array and depth == 2:
            in_bag = False
        elif in_codes:
            builder.event(event, value)
        elif in_bag:
            if not building_bag_item and is_start:
                builder.event(event, value)
                building_bag_item = True
            elif building_bag_item and is_end:
                builder.event(event, value)
                building_bag_item = False
            elif building_bag_item:
                builder.event(event, value)
            else:
                if codes:
                    chain.add_to_bag(codes[start], (codes[i] for i in builder.value), count=value)
                else:
                    chain.add_to_bag(start, builder.value, count=value)
