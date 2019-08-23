from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request

def api_v1_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "api_v1")