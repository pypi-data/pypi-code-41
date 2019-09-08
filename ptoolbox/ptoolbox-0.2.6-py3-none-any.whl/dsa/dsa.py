import codecs
import os
from helpers.clog import CLog


def create_problem(folder, problem_code, overwrite=False):
    problem_code = problem_code.replace('-', '_').replace(' ', '_').lower()

    problem_folder =  os.path.join(folder, problem_code)

    if os.path.exists(problem_folder):
        if not overwrite:
            CLog.error('Problem folder existed! Delete the folder or use `overwrite` instead.')
            return
        else:
            CLog.warn('Problem folder existed! Content will be overwritten.')

    if not os.path.exists(problem_folder):
        os.makedirs(problem_folder)

    # if not os.path.exists(problem_folder + "/testcases"):
    #     os.makedirs(problem_folder + "/testcases")

    problem_name = (' '.join(problem_code.split('_'))).title()

    f = codecs.open(problem_folder + ("/%s.md" % problem_code), "w", "utf-8")
    f.write(
        f"""[//]: # (http://source.link)
[//]: # (hackerrank_id: )  

# {problem_name}
[//]: # ({problem_code})

Nhập vào `3` số nguyên `B`, `P`, `M`. Hãy tính:

$$R = B^P \mod M$$   
 
## Input

- Dòng đầu chứa số tự nhiên `T` - số lượng các testcase
- `T` dòng sau, mỗi dòng chứa `3` số nguyên không âm `B`, `P`, `dM`.

## Constraints

- $0 ≤ B, P ≤ 2^{{31}} - 1$
- $1 ≤ M ≤ 46340$

## Output

`1` số `R` là kết quả phép tính $R = B^P \mod M$

## Tags

- Number Theory 
- Recursion

## Sample input 1

```
3 18132 17  
```

## Sample output 1

```
13
```

## Explanation 1

Giải thích cho sample test case 1
""")

    f.close()

    open(problem_folder + "/testcases.txt", 'w').close()
    f = open(problem_folder + "/testcases_manual.txt", 'w')
    f.write("""### 0
input 0
---
output 0
### 1
input 1
---
output 1
### 2
input 2
---
output 2
""")
    f.close()

    f = open(problem_folder + ("/%s.py" % problem_code), 'w')
    f.write(
        f"""def pmod(a, b, mod):
	if b == 0:
		return 1
	res = pmod(a, int(b / 2), mod)
	res = (res * res) % mod
	if b % 2 == 1:
		return (res * a) % mod
	return res


def {problem_code}(b, p, m):
	return pmod(b, p, m)


if __name__ == "__main__":
	[b, p, m] = map(int, input().split())
	result = {problem_code}(b, p, m)
	print(result)
""")
    f.close()

    f = open(problem_folder + ("/%s_generator.py" % problem_code), 'w')
    f.write(
        ("""from contextlib import redirect_stdout
from helpers.clog import CLog
from helpers.crandom import CRandom


manual_tests_input = [
	(3, 18132, 17),
	(17, 1765, 3),
	(2374859, 3029382, 36123)
]

test_number = 0

CLog.echo("Writing manual testcases...")

with open('testcases_manual.txt', "w") as f:
	with redirect_stdout(f):
		for test in manual_tests_input:
			print(f"### {test_number} - manual")
			print(*test)
			print("---")
			result = %s(*test)
			print(result)
			test_number += 1

CLog.echo("DONE")
CLog.echo("Generating testcases...")

NUMBER_OF_TESTCASES = 20
test_number = 0
with open('testcases.txt', "w") as f:
	with redirect_stdout(f):
		for test in range(NUMBER_OF_TESTCASES):
			if test < 5:
				vmax = 100
			elif test < 10:
				vmax = 100000
			elif test < 15:
				vmax = 1000000
			else:
				vmax = 2**31-1

			a = CRandom.int(0, vmax)
			b = CRandom.int(0, vmax)
			m = CRandom.int(1, 46340)

			print(f"### {test_number}")
			print(a, b, m)
			print("---")
			result = %s(a, b, m)
			print(result)
			test_number += 1
CLog.echo("DONE")

""" % (problem_code, problem_code))
    )
    f.close()

    problem_folder = os.path.abspath(problem_folder)

    CLog.important(f'Problem created at `{problem_folder}`')


def read_testcases_from_file(testcase_file):
    count = 0
    inputi = ""
    outputi = ""
    is_output = False

    testcases = []

    with open(testcase_file, 'r') as fi:
        for line in fi:
            if line.startswith("###"):

                if count > 0:
                    testcases.append({'input': inputi.strip(), 'output': outputi.strip()})

                count += 1

                is_output = False

                inputi = outputi = ""

                continue
            elif line.startswith("---"):
                is_output = True
            else:
                if is_output:
                    outputi += line
                else:
                    inputi += line

        testcases.append({'input': inputi.strip(), 'output': outputi.strip()})

    return testcases


if __name__ == '__main__':
    create_problem('../problems', 'Array001 Counting-Sort2', overwrite=True)

    # tcs = read_testcases_from_file('../problems/prob1/testcases.txt')
    # print(*tcs, sep='\n')
