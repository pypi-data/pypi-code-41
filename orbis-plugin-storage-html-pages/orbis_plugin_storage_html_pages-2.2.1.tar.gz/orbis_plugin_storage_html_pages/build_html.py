from operator import itemgetter
import os

from .templates.arrow_key_navigation import arrow_key_navigation as arrow_key_navigation_template
from .templates.bootstrap_core_css import bootstrap_core_css as bootstrap_core_css_template
from .templates.bootstrap_core_js import bootstrap_core_js as bootstrap_core_js_template
from .templates.html_css import html_css as html_css_template
from .templates.navigation_js import navigation_js as navigation_js_template

from .templates.html_body import html_body as html_body_template
from .templates.navigation import navigation as navigation_template
from .templates.orbis_header import orbis_header as orbis_header_template
from .templates.item_header import item_header as item_header_template
from .templates.gold_corpus import gold_corpus as gold_corpus_template
from .templates.gold_entities import gold_entities as gold_entities_template
from .templates.predicted_corpus import predicted_corpus as predicted_corpus_template
from .templates.predicted_entities import predicted_entities as predicted_entities_template


def get_gold_entities(rucksack, item, sf_colors, gold_html):

    gold_entities = []
    if len(item['gold']) > 0:
        last_start = int(len(item['corpus']))
        last_end = int(len(item['corpus']))
        # last_word = ""
        for entity in sorted(item['gold'], key=itemgetter("end"), reverse=True):
            entity_types = rucksack.result_summary(specific='binary_classification')['entities']

            if entity['entity_type'] not in entity_types and len(entity_types) > 0:
                continue

            start_tag = '<abbr title="{}" style="background-color:{};">'.format(
                entity['key'],
                sf_colors[entity['key']]
            )
            end_tag = '</abbr>'
            if int(entity['start']) <= int(last_start):
                if int(entity['start']) < int(last_end):
                    entity_start = int(entity['start'])
                else:
                    entity_start = False
                    # case = 1
                    # print("{}\t-\t{}: {} (1)\n{}\t-\t{}: {}".format(entity['start'], entity['end'], entity['surfaceForm'], last_start, last_end, last_word))
            else:
                entity_start = False
                # case = 2
                # print("{}\t-\t{}: {} (2)\n{}\t-\t{}: {}".format(entity['start'], entity['end'], entity['surfaceForm'], last_start, last_end, last_word))
            if int(entity['end']) < int(last_end):
                if int(entity['end']) < int(last_start):
                    entity_end = int(entity['end'])
                else:
                    entity_end = False
                    # case = 3
                    # print("{}\t-\t{}: {} (3)\n{}\t-\t{}: {}".format(entity['start'], entity['end'], entity['surfaceForm'], last_start, last_end, last_word))
            else:
                entity_end = False
                # case = 4
                # print("{}\t-\t{}: {} (4)\n{}\t-\t{}: {}".format(entity['start'], entity['end'], entity['surfaceForm'], last_start, last_end, last_word))
            if isinstance(entity_start, int) and entity_end:
                gold_html = gold_html[:int(entity['end'])] + end_tag + gold_html[int(entity['end']):]
                gold_html = gold_html[:int(entity['start'])] + start_tag + gold_html[int(entity['start']):]
            else:
                if len(entity['key']) > 0:
                    overlap_warning = '<abbr title="{}" style="background-color:{};"><b>&#x22C2;</b></abbr>'.format(
                        entity['key'],
                        sf_colors[entity['key']]
                    )
                    gold_html = gold_html[:int(last_start)] + overlap_warning + gold_html[int(last_start):]
                    # print("-{}-> {}\t-\t{}: {}\n{}\t-\t{}: {}".format(case, entity['start'], entity['end'], entity['surfaceForm'], last_start, last_end, last_word))
            last_start = entity_start or last_start
            last_end = entity_end or last_end
            # last_word = entity['surfaceForm']
            gold_entities.append({
                "surfaceForm": entity['surfaceForm'],
                "key": entity['key'],
                "start": entity['start'],
                "end": entity['end'],
                "entity_type": entity['entity_type'],
                "background": sf_colors[entity['key']]})
    return gold_entities, gold_html


def get_predicted_entities(config, rucksack, item, sf_colors, predicted_html):

    predicted_entities = []
    if len(item['computed']) > 0:
        last_start = len(item['corpus'])
        last_end = len(item['corpus'])
        # last_word = ""
        for e_idx, entity in enumerate(sorted(item['computed'], key=itemgetter("document_end"), reverse=True)):
            entity_types = config['scoring'].get('entities', [])

            # print(entity['entity_type'] not in entity_types and len(entity_types) > 0)
            if entity['entity_type'] not in entity_types and len(entity_types) > 0:
                continue
            is_fp = False
            entity_id = "{},{}".format(entity['document_start'], entity['document_end'])
            is_fp = True if entity_id in rucksack.resultview(item['index'], specific="binary_classification")['confusion_matrix']['fp_ids'] else False
            if is_fp:
                start_tag = '<abbr title="{}" style="background-color:{}"><s>'.format(entity['key'], sf_colors[entity['key']])
                end_tag = '</s></abbr>'
            else:
                start_tag = '<abbr title="{}" style="background-color:{}">'.format(entity['key'], sf_colors[entity['key']])
                end_tag = '</abbr>'
            if int(entity['document_start']) <= int(last_start):
                if int(entity['document_start']) < int(last_end):
                    entity_start = int(entity['document_start'])
                else:
                    entity_start = False
                    # case = 1
                    # print("{}\t-\t{}: {} (1)\n{}\t-\t{}: {}".format(entity['document_start'], entity['document_end'], entity['surfaceForm'], last_start, last_end, last_word))
            else:
                entity_start = False
                # case = 2
                # print("{}\t-\t{}: {} (2)\n{}\t-\t{}: {}".format(entity['document_start'], entity['document_end'], entity['surfaceForm'], last_start, last_end, last_word))
            if int(entity['document_end']) < int(last_end):
                if int(entity['document_end']) < int(last_start):
                    entity_end = int(entity['document_end'])
                else:
                    entity_end = False
                    # case = 3
                    # print("{}\t-\t{}: {} (3)\n{}\t-\t{}: {}".format(entity['document_start'], entity['document_end'], entity['surfaceForm'], last_start, last_end, last_word))
            else:
                entity_end = False
                # case = 4
                # print("{}\t-\t{}: {} (4)\n{}\t-\t{}: {}".format(entity['document_start'], entity['document_end'], entity['surfaceForm'], last_start, last_end, last_word))
            if isinstance(entity_start, int) and entity_end:
                predicted_html = predicted_html[:int(entity['document_end'])] + end_tag + predicted_html[int(entity['document_end']):]
                predicted_html = predicted_html[:int(entity['document_start'])] + start_tag + predicted_html[int(entity['document_start']):]
            else:
                if len(entity['key']) > 0:
                    if is_fp:
                        overlap_warning = '<abbr title="{}" style="background-color:{};"><s><b>&#x22C2;</b></s></abbr>'.format(entity['key'], sf_colors[entity['key']])
                    else:
                        overlap_warning = '<abbr title="{}" style="background-color:{};"><b>&#x22C2;</b></abbr>'.format(entity['key'], sf_colors[entity['key']])
                    predicted_html = predicted_html[:int(last_start)] + overlap_warning + predicted_html[int(last_start):]
                    # print("[orbis] -{}-> {}\t-\t{}: {}\n{}\t-\t{}: {}".format(case, entity['document_start'], entity['document_end'], entity['surfaceForm'], last_start, last_end, last_word))
            last_start = entity_start or last_start
            last_end = entity_end or last_end
            # last_word = entity['surfaceForm']
            predicted_entities.append({
                "surfaceForm": entity['surfaceForm'],
                "key": entity['key'],
                "start": entity['document_start'],
                "end": entity['document_end'],
                "entity_type": entity['entity_type'],
                "background": sf_colors[entity['key']]})
    return predicted_entities, predicted_html


def get_top_header(config, rucksack):

    top_header_0 = {
        "aggregator_name": config['aggregation']['service']['name'],
        "aggregator_profile": config['aggregation']['service'].get("profile", "None"),
        "aggregator_limit": config['aggregation']['service'].get("limit", "None"),
        "aggregator_location": config['aggregation']['service']['location']
    }
    top_header_1 = {
        "aggregator_data_set": config['aggregation']['input']['data_set']['name'],
        "evaluator_name": config['evaluation']['name'],
        "scorer_name": config['scoring']['name'],
        "entities": ", ".join([e for e in rucksack.result_summary(specific='binary_classification')['entities']])
    }
    top_header_2 = {
        "has_score": rucksack.result_summary(specific='binary_classification')['has_score'],
        "no_score": rucksack.result_summary(specific='binary_classification')['no_score'],
        "empty_responses": rucksack.result_summary(specific='binary_classification')['empty_responses']
    }
    micro_precision = f"{rucksack.result_summary(specific='binary_classification')['micro']['precision']:.3f}"
    macro_precision = f"{rucksack.result_summary(specific='binary_classification')['macro']['precision']:.3f}"
    micro_macro_precision = "(" + "/".join([str(micro_precision), str(macro_precision)]) + ")"
    micro_recall = f"{rucksack.result_summary(specific='binary_classification')['micro']['recall']:.3f}"
    macro_recall = f"{rucksack.result_summary(specific='binary_classification')['macro']['recall']:.3f}"
    micro_macro_recall = "(" + "/".join([str(micro_recall), str(macro_recall)]) + ")"
    micro_f1_score = f"{rucksack.result_summary(specific='binary_classification')['micro']['f1_score']:.3f}"
    macro_f1_score = f"{rucksack.result_summary(specific='binary_classification')['macro']['f1_score']:.3f}"
    micro_macro_f1_score = "(" + "/".join([str(micro_f1_score), str(macro_f1_score)]) + ")"
    top_header_3 = {
        "precision": micro_macro_precision,
        "recall": micro_macro_recall,
        "f1_score": micro_macro_f1_score,
    }
    header_html_0 = """
    <b>Aggregator Name:</b>\t{aggregator_name}</br>
    <b>Aggregator Profile:</b>\t{aggregator_profile}</br>
    <b>Aggregator Limit:</b>\t{aggregator_limit}</br>
    <b>Aggregator Service:</b>\t{aggregator_name}</br>
    """.format(**top_header_0)
    header_html_1 = """
    <b>Aggregator Dataset:</b>\t{aggregator_data_set}</br>
    <b>Evaluator Name:</b>\t{evaluator_name}</br>
    <b>Scorer Name:</b>\t{scorer_name}</br>
    <b>Entities:</b>\t{entities}</br>
    """.format(**top_header_1)
    header_html_2 = """
    <b>Some Score:</b>\t{has_score}</br>
    <b>No Score:</b>\t{no_score}</br>
    <b>Empty Responses:</b>\t{empty_responses}</br>
    """.format(**top_header_2)
    header_html_3 = """
    <b>Precision (micro/macro):</b>\t{precision}</br>
    <b>Recall (micro/macro):</b>\t{recall}</br>
    <b>F1 Score (micro/macro):</b>\t{f1_score}</br>

    """.format(**top_header_3)
    return header_html_0, header_html_1, header_html_2, header_html_3


def get_item_header(rucksack, key):

    item_header_0 = {
        "precision": rucksack.resultview(key, specific='binary_classification')['precision'],
        "recall": rucksack.resultview(key, specific='binary_classification')['recall'],
        "f1_score": rucksack.resultview(key, specific='binary_classification')['f1_score']
    }
    item_header_1 = {
        "tp": sum(rucksack.resultview(key, specific='binary_classification')['confusion_matrix']['tp']),
        "fp": sum(rucksack.resultview(key, specific='binary_classification')['confusion_matrix']['fp']),
        "fn": sum(rucksack.resultview(key, specific='binary_classification')['confusion_matrix']['fn'])
    }

    header_html_0 = """
    <b>Precision:</b>\t{precision:.3f}</br>
    <b>Recall:</b>\t{recall:.3f}</br>
    <b>F1 Score:</b>\t{f1_score:.3f}</br>
    """.format(**item_header_0)

    header_html_1 = """
    <b>True Positives:</b>\t{tp}</br>
    <b>False Positives:</b>\t{fp}</br>
    <b>False Negatives:</b>\t{fn}</br>
    """.format(**item_header_1)
    return header_html_0, header_html_1


def get_gold_html(rucksack, item, sf_colors):

    gold_html = item['corpus']
    gold_entities, gold_html = get_gold_entities(rucksack, item, sf_colors, gold_html)
    gold_entities_html = ""
    for entity in list(reversed(gold_entities)):
        gold_entities_html += '<p><span style="background-color:{background};"><b>{surfaceForm}</b></span> (<a href="{key}">{key}</a>): {start} - {end}: {entity_type}</p>'.format(**entity)
    return gold_html, gold_entities_html


def get_predicted_html(config, rucksack, item, sf_colors):

    predicted_html = item['corpus']
    predicted_entities, predicted_html = get_predicted_entities(config, rucksack, item, sf_colors, predicted_html)
    predicted_entities_html = ""
    for entity in list(reversed(predicted_entities)):
        predicted_entities_html += '<p><span style="background-color:{background};"><b>{surfaceForm}</b></span> (<a href="{key}">{key}</a>): {start} - {end}: {entity_type}</p>'.format(**entity)
    return predicted_html, predicted_entities_html


def get_next_button(key):

    if key:
        next_item = os.path.join(str(key) + ".html")

        next_button = """<p><a id="next_page_link" class="btn btn-secondary" href="{url}" role="button" style="float: right;">Next Item &raquo;</a></p>""".format(url=next_item)
    else:
        next_button = ""
    return next_button


def get_previous_button(key):

    if key:
        previous_item = os.path.join(str(key) + ".html")
        previous_button = """<p><a id="previous_page_link" class="btn btn-secondary" href="{url}" role="button">&laquo; Previous Item</a></p>""".format(url=previous_item)
    else:
        previous_button = ""
    return previous_button


def build_blocks(config, rucksack, item, next_item, previous_item, sf_colors):

    key = item['index']

    orbis_column_0, orbis_column_1, orbis_column_2, orbis_column_3 = get_top_header(config, rucksack)
    orbis_header = orbis_header_template.format(
        orbis_column_0=orbis_column_0,
        orbis_column_1=orbis_column_1,
        orbis_column_2=orbis_column_2,
        orbis_column_3=orbis_column_3
    )

    item_column_0, item_column_1 = get_item_header(rucksack, key)
    item_header = item_header_template.format(
        item_number=key,
        item_column_0=item_column_0,
        item_column_1=item_column_1
    )

    gold_html, gold_entities_html = get_gold_html(rucksack, item, sf_colors)
    gold_corpus = gold_corpus_template.format(gold_html=gold_html)
    gold_entities = gold_entities_template.format(gold_entities_html=gold_entities_html)

    predicted_html, predicted_entities_html = get_predicted_html(config, rucksack, item, sf_colors)
    predicted_corpus = predicted_corpus_template.format(predicted_html=predicted_html)
    predicted_entities = predicted_entities_template.format(predicted_entities_html=predicted_entities_html)

    previous_button = get_previous_button(previous_item)
    next_button = get_next_button(next_item)
    navigation = navigation_template.format(prev=previous_button, next=next_button)

    html_item_dict = {
        'orbis_header': orbis_header,
        'item_header': item_header,
        'gold_corpus': gold_corpus,
        'gold_entities': gold_entities,
        'predicted_corpus': predicted_corpus,
        'predicted_entities': predicted_entities,
        'navigation': navigation,
        'arrow_key_navigation': arrow_key_navigation_template,
        'bootstrap_core_css': bootstrap_core_css_template,
        'bootstrap_core_js': bootstrap_core_js_template,
        'html_css': html_css_template,
        'navigation_js': navigation_js_template
    }

    return html_item_dict


def build_page(html_item_dict):
    html = html_body_template.format(**html_item_dict)
    return html


def build(config, rucksack, item, next_item, previous_item, sf_colors):
    html_blocks = build_blocks(config, rucksack, item, next_item, previous_item, sf_colors)
    html = build_page(html_blocks)
    return html, html_blocks
