#read functions from bottom to up
import sys,json

def sort_by_values(obj,reverse=True):
	return dict(sorted(obj.items(),key=lambda key_value:key_value[1],reverse=reverse)) if obj else obj
sort_by_value=sort_by_values

def weight_in(subset,mainset):
	res={}
	for k,v in subset.items():
		if k in mainset:
			res[k]=subset[k]/mainset[k]
	return res

def freq(arr):
	res={}
	for word in arr:
		if word in res:
			res[word]+=1
		else:
			res[word]=1
	return res
def normalize(res):
	total=sum(v for k,v in res.items())
	for word in res:
		res[word]=res[word]/total
	return res

def vectorize(text,permitted=None):
	if not permitted:
		permitted="qwertyuiopasdfghjklzxcvbnm"
		permitted+=permitted.upper()
	arr=list(map(lambda c: c if c in permitted else " ",list(text.lower())))
	text="".join(arr)
	while "  " in text:
		text=text.replace("  "," ")
	arr=text.split(' ')
	return normalize(freq(arr))

def tf_idf(context,text):
	return weight_in(normalize(context) if type(context)==dict else vectorize(context),normalize(text) if type(text)==dict else vectorize(text))

if __name__ == "__main__":
	text=open(sys.argv[2],"r+").read() if sys.argv[1].endswith(".txt") else sys.argv[1]
	context=open(sys.argv[1],"r+").read() if sys.argv[1].endswith(".txt") else sys.argv[2]
	print(json.dumps(sort_by_values(tf_idf(context,text),reverse=True),indent=4))

