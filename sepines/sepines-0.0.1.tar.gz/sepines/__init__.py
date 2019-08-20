def max_chars(text, lines):
	text = list(text)
	vezes = len(text)/lines
	if vezes > 1 or vezes ==1:
		vezes = (round(vezes))+1
	else:
		vezes = 0
	for i in range(vezes):
		text.insert((lines*i), '\n')
	text = ''.join(text)
	print(text)
def max_words(text, lines):
	lines += 1
	text = text.split()
	vezes = len(text)/lines
	if vezes > 1 or vezes ==1:
		vezes = (round(vezes))+2
	else:
		vezes = 0
	for i in range(vezes):
		text.insert((lines*i), '\n')
	text = ' '.join(text)
	print(text)


