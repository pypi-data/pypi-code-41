from base64 import b64decode
from .attack_single_byte_xor import single_byte_xor_exlude_nonprintables
from ..cipher.cipher_repeating_key_xor import repeating_xor

def get_hamming_distance(byte_string1, byte_string2):
	if len(byte_string1) != len(byte_string2):
		raise Exception('Input lengths not equal.')
	hex_string1,hex_string2 = hexlify(byte_string1),hexlify(byte_string2)
	binary_xored = format(int(hex_string1, 16) ^ int(hex_string2, 16), 'b')
	return len(list(filter(lambda c: c == '1', binary_xored)))

# We test with the first 8 blocks and average the hamming distances of 28
# pairs to find the most probable key_size. This will return an array of
# the 3 key sizes with min hamming distances.
def repeating_xor_guess_key_size(ciphertext, max_key_size=50, num_blocks=8):
	if max_key_size * num_blocks > len(ciphertext):
		raise Exception('Input length too small')
	avg_hamming_distances = []
	for key_size in range(2,max_key_size+1):
		blocks = []
		for i in range(num_blocks):
			blocks.append(ciphertext[i*key_size:(i+1)*key_size+1])
		hamming_distances = []
		for i in range(len(blocks)):
			for j in range(i+1,len(blocks)):
				hamming_distances.append(
					get_hamming_distance(blocks[i],blocks[j]))
		avg_hamming_distances.append((key_size,
			sum(hamming_distances) / len(hamming_distances) / key_size))
	avg_hamming_distances.sort(key=lambda x: x[1])
	return list(map(lambda x: x[0], avg_hamming_distances[:3]))

def repeating_xor_guess_key(ciphertext, key_size=-1, alpha=0.000001, normal_rate=0.8):
	if key_size < 0:
		key_size = repeating_xor_guess_key_size(ciphertext)
	transposed_blocks = [b'' for _ in range(key_size)]
	for i in range(len(ciphertext)):
		transposed_blocks[i%key_size] += bytes([ciphertext[i]])
	#transposed_blocks = list(map(
	#	lambda x: x.encode('utf-8'), transposed_blocks))
	keys = []
	for block in transposed_blocks:
		guess_solns = single_byte_xor_exlude_nonprintables(
			block,alpha,normal_rate)
		if len(guess_solns):
			keys.append(guess_solns[0][2])
		else:
			keys.append(b'?')
	print(keys)
	return b''.join(keys)
	#return key.encode('utf-8')