
unit_translations = { 1:       '',
		      10:      'In tens',
		      100:     'In hundreds',
		      1000:    'In thousands',
		      10000:   'In 10,000s',
		      100000:  'In 100,000s',
		      1000000: 'In millions' }

unit_choices = [1000000, 100000, 10000, 1000, 100, 10, 1]

desired_brackets = 5
base_round_numbers = (5, 10, 15, 20, 25)

def find_round_dividend(mx):
    if mx < desired_brackets:
	return 1

    nseeds = len(base_round_numbers)
    def gen_round_number():
	m = 1
	i = 0
	while 1:
	    yield m * base_round_numbers[i % nseeds]
	    i += 1
	    if i % nseeds == 0:
		m *= 10
	return

    closest_distance = None
    closest = None
    for n in gen_round_number():
	brackets = mx / n
	distance = abs(brackets - desired_brackets)
	if closest_distance is None or distance < closest_distance:
	    closest_distance = distance
	    closest = n
	if n > mx:
	    break
    
    return closest
    
def get_labels(mx):
    d = find_round_dividend(mx)
    n = (mx / d) + 1
    labels = []
    brackets = []
    units = 1
    for units in unit_choices:
	if d % units == 0:
	    i = 1
	    while i <= n:
		x = d * i
		labels.append("%d" % (x / units))
		brackets.append(x)
		i += 1	
	    break
    return (zip(labels, brackets), unit_translations[units])

def test_find_round():

    for n in [ -1, 0, 8.4, 10, 13, 25, 42, 75, 125, 127, 528, 3016, 10001 ]:
	d = find_round_dividend(n)
	if d:
	    print str(n), d, n / d

    return

def test_find_round_rand():
    import random

    for i in range(10):
	n = random.randint(0, 500000)
	print n, "..."
	d = find_round_dividend(n)
	print n, d, n / d

    return

def test_find_labels():
    import random

    for i in range(10):
	n = random.randint(0, 500000)
	print n, "..."
	labels = get_labels(n)
	print n, labels

    return

def main():
    test_find_labels()
    return

if __name__ == '__main__':
    main()
