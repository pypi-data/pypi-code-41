from kivy.metrics import sp

fontSize = {
	"small":12,
	"normal":16,
	"large":20,
	"huge":24,
}

def getFontSize():
	return normalfontsize

def textsize(x):
	return (sp(x * getFontSize()), sp(getFontSize()))

def buttonsize(x):
	m = 2 * sepertorsize
	return (sp(textsize(x)+m),sp(getFontSize()+m))

def inputlinesize(x):
	m = 2 * sepertorsize
	return (sp(x * getFontSize()+m), sp(getFontSize()+m))

