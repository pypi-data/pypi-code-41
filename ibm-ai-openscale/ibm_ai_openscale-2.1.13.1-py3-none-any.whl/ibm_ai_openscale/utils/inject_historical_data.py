import os
import json
import requests
from ibm_ai_openscale.client import APIClient
from ibm_ai_openscale.utils.href_definitions_v2 import AIHrefDefinitionsV2
from datetime import datetime, timedelta


def load_historical_kpi_measurement(file_path, aios_credentials, monitor_instance_id, business_application_id, day_template="history_payloads_{}.json", days=7, batch_id_start=0, ignore_metrics=None):
    hrefs_v2 = AIHrefDefinitionsV2(aios_credentials)
    ai_client = APIClient(aios_credentials)

    with open(file_path) as json_file:
        historical_kpi = json.load(json_file)

    measurement = historical_kpi['history_payloads_0.json'][0]
    metric_names = [metric['id'] for metric in measurement['metrics']]

    monitor_details = requests.get(
        url=hrefs_v2.get_monitor_instance_details_href(monitor_instance_id),
        headers=ai_client._get_headers()
    )

    assert 200 == monitor_details.status_code
    monitor_details = monitor_details.json()
    monitor_definition_id = monitor_details['entity']['monitor_definition_id']

    monitor_definition_details = requests.get(
        url=hrefs_v2.get_monitor_definitions_details_href(monitor_definition_id),
        headers=ai_client._get_headers()
    )

    assert 200 == monitor_definition_details.status_code

    monitor_definition_details = monitor_definition_details.json()
    tags = monitor_definition_details['entity']['tags']

    bapp_details = requests.get(
        url=hrefs_v2.get_application_details_href(business_application_id),
        headers=ai_client._get_headers()
    )

    if bapp_details.status_code != 200:
        raise Exception("Unable to get business app details. Reason {}".format(bapp_details.text))

    bapp_details = bapp_details.json()
    business_metrics_ids = [b_metric['name'] for b_metric in bapp_details['entity']['business_metrics']]

    payload = []

    batch_id_number = batch_id_start

    for day in range(0, days):
        payload_day_json = day_template.format(day)
        if payload_day_json in historical_kpi.keys():
            for h_measurements in historical_kpi[payload_day_json]:
                metrics_dict = {}
                for tag in tags:
                    if 'batch_id' in tag['id']:
                        metrics_dict[tag['id']] = "batch-id-{}".format(batch_id_number)
                    # elif "business_application_id" == tag['id']:
                    #     metrics_dict["business_application_id"] = business_application_id
                    # elif "business_metric_id" == tag['id']:
                    #     metrics_dict["business_metric_id"] = business_metric

                for name in metric_names:
                    for h_metric in h_measurements['metrics']:
                        if name == h_metric['id']:
                            if ignore_metrics is None or name not in ignore_metrics:
                                metrics_dict[name] = h_metric['value']

                current_time = datetime.utcnow().isoformat() + 'Z'
                start_time = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(hours=batch_id_number)
                start_time = start_time.isoformat() + 'Z'

                payload.append({
                    "timestamp": str(start_time),
                    "metrics": [metrics_dict]
                })

                batch_id_number += 1

    response = requests.post(
        url=hrefs_v2.get_measurements_href(monitor_instance_id),
        headers=ai_client._get_headers(),
        json=payload)

    print('***', response.status_code, response.text)

    assert 202 == response.status_code


def load_historical_payload(file_path, aios_credentials, data_set_id, day_template="history_payloads_{}.json", days=7, batch_id_start=0):
    hrefs_v2 = AIHrefDefinitionsV2(aios_credentials)
    ai_client = APIClient(aios_credentials)

    with open(file_path) as json_file:
        historical_data = json.load(json_file)

    payload = []
    for day in range(0, days):
        fields = historical_data[day_template.format(day)][0]['fields']
        for value in historical_data[day_template.format(day)][0]['values']:
            payload.append({
                fields[0]: value[0],
                fields[1]: value[1],
                fields[2]: value[2],
                fields[3]: value[3],
                fields[4]: value[4]
            })

    response = requests.post(
        url=hrefs_v2.get_data_set_records_href(data_set_id),
        headers=ai_client._get_headers(),
        json=payload)

    assert response.status_code == 202


def load_historical_drift_measurement(file_path, aios_credentials, monitor_instance_id, business_application_id, day_template="history_payloads_{}.json", days=7, batch_id_start=0):
    hrefs_v2 = AIHrefDefinitionsV2(aios_credentials)
    ai_client = APIClient(aios_credentials)

    with open(file_path) as json_file:
        historical_drift = json.load(json_file)

    payload = []


    # Mock for correlations
    bkpis_file_path = os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'historical_records', 'history_kpi.json')

    with open(bkpis_file_path) as json_file:
        historical_bkpis = json.load(json_file)
    # --------- end of mock -----------

    batch_id_number = batch_id_start

    for day in range(0, days):
        for h_measurements, kpi_measurement in zip(historical_drift[day_template.format(day)], historical_bkpis[day_template.format(day)]):
            acc = [metric['value']/600 for metric in kpi_measurement['metrics'] if metric['id'] == 'number_accepted'][0]
            payload.append({
                "timestamp": h_measurements['ts'],
                "metrics": [{
                    'drift_magnitude': 1 - acc,
                    'predicted_accuracy': acc,
                    'transaction_batch_id': "batch-id-{}".format(batch_id_number),
                    'business_application_id': business_application_id,
                    'business_metric_id': ""
                }]
            })
            batch_id_number += 1

    response = requests.post(
        url=hrefs_v2.get_measurements_href(monitor_instance_id),
        headers=ai_client._get_headers(),
        json=payload)
    assert response.status_code == 202