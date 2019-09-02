def message_value(message, info, value):
	counter_message = {}
	counter_message ['counter_message'] = message
	counter_message['counter_value'] = value
	if info:
		counter_message['info'] =  info
	return counter_message
