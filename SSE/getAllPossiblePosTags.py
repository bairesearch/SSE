import nltk
from nltk.corpus import brown
from collections import Counter, defaultdict

# x is a dict which will have the word as key and pos tags as values 
x = defaultdict(list)


def main():
	constructPOSdictionary()
	posValues = getAllPossiblePosTags('run')
	print(posValues)
	#['VB', 'NN', 'VBN', 'VBD']
	# 
	# VB: run the procedure
	# NN: the run
	# VBN: (passive) past participle - it was run
	# VBD: ??? - shouldnt this be ran? [https://stackoverflow.com/questions/51722351/get-all-possibles-pos-tags-from-a-single-word]

def constructPOSdictionary():
	for word, pos in brown.tagged_words():
		if pos not in x[word]:		# to append one tag only once
			x[word].append(pos)
				
def getAllPossiblePosTags(wordTest):
	posValues = x[wordTest]
	return posValues

if __name__ == '__main__':
	main()
