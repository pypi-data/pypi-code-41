
def get_calls_id_to_function_map(live_values):
    call_id_to_funciton = {}
    for filename in live_values.keys():
        for function_name in live_values[filename].keys():
            for call_id in live_values[filename][function_name]['calls'].keys():
                call_id_to_funciton[call_id] = [filename, function_name]
    return call_id_to_funciton
