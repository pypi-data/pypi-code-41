# Xor the message with a key stream. The message and the key need to be of
# equal length. (This is one time pad, a perfectly correct crypto scheme)
#
# Parameters:
#	m - message in bytes; if expressed in string, we convert it to bytes
#	k - keystream in bytes; if expressed in string, we convert it to bytes
#
# Returns:
#	A bytes object consisting of xors of each byte of m and k
def xor(m, k):
	if isinstance(m, str):
		m = m.encode('utf-8')
	if isinstance(k, str):
		k = k.encode('utf-8')

	return bytes([m[i]^k[i] for i in range(len(m))])
