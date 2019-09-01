from edc_list_data import PreloadData


model_data = {
    "edc_lab.consignee": [
        {
            "name": "LSTM",
            "contact_name": "-",
            "address": "-",
            "postal_code": "-",
            "city": "-",
            "state": "-",
            "country": "-",
            "telephone": "-",
            "mobile": "-",
            "fax": "-",
            "email": "",
        }
    ]
}

unique_field_data = {"edc_lab.consignee": {"name": ("-", "-")}}

preload_data = PreloadData(
    list_data=None, model_data=model_data, unique_field_data=unique_field_data
)
