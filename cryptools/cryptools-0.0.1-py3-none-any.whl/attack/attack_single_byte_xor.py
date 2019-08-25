# TODO: Include variants for spaces, symbols, and other languages.
from scipy.stats import chisquare
from binascii import unhexlify

letter_relative_freq = [0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074]
normal_ascii = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \n.,_\'\"'
alphabet = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Take in a hex string, return a list of candidates (byte string, p val tuples)
def single_byte_xor(byte_string, alpha=0.01):
	candidates = []
	for test_byte in range(256):
		xored_string = b''
		for byte in byte_string:
			xored_string += bytes([test_byte ^ byte])

		obs_freq = [0 for _ in range(26)]
		for c in xored_string:
			pos = alphabet.find(c)
			if pos >= 0:
				obs_freq[pos % 26] += 1

		total_letters = sum(obs_freq)
		if total_letters == 0:
			continue

		exp_freq = [total_letters * letter_relative_freq[i] for i in range(26)]

		p_val = chisquare(f_obs=obs_freq, f_exp=exp_freq)[1]
		if p_val <= alpha:
			continue

		candidates.append((
			xored_string, 
			p_val,
			bytes([test_byte])
		))
	
	candidates.sort(key=lambda cand:cand[1], reverse=True)
	return candidates

def single_byte_xor_exlude_nonprintables(
	byte_string, 
	alpha=0.01, 
	normal_rate=0.8
):
	candidates = single_byte_xor(byte_string, alpha)
	real_candidates = []
	for candidate in candidates:
		num_normal_chars = 0
		for c in candidate[0]:
			if c in normal_ascii:
				num_normal_chars += 1
		if num_normal_chars / len(candidate[0]) >= normal_rate:
			real_candidates.append(candidate)
	return real_candidates