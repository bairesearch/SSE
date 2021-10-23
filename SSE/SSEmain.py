"""SSEmain.py

# Author:
Richard Bruce Baxter - Copyright (c) 2021 Baxter AI (baxterai.com)

# License:
MIT License

# Installation:
pip install nltk

# Usage:
python SSEmain.py

# Description:
SSE - syntactical structure extraction

"""

from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict

wordStructureClassDictionaryFirst = defaultdict(list)	#indexed by first word in wordStructure
wordStructureClassDictionaryLast = defaultdict(list)	#indexed by last word in wordStructure

SSEmatchSurroundStructure = 1
SSEmatchFirstStructure = 2
SSEmatchLastStructure = 3

substructureSideNA = 0
substructureSideRight = 1
substructureSideLeft = 2

substructureLinkTypeNA = 0
substructureLinkTypeInsertion = 1
substructureLinkTypeReplacement = 2

SSErecurse = True

nodeTypeWord = True
nodeTypeSubstructure = False

class wordStructureNodeValueClass():
	def __init__(self, content, nodeType, substructureSide, substructureLinkType):
		self.content = content	#either word or wordStructureClass (depending on nodeType)
		self.nodeType = nodeType
		self.substructureSide = substructureSide
		self.substructureLinkType = substructureLinkType
			
class wordStructureNodeClass():
	def __init__(self, value, nodeType, substructureSide, substructureLinkType):
		self.possibleValues = []
		wordStructureNodeValue = wordStructureNodeValueClass(value, nodeType, substructureSide, substructureLinkType)
		self.possibleValues.append(wordStructureNodeValue)	
		
class wordStructureClass():
	def __init__(self, wordStructureTokens):
	
		self.wordStructureNodes = []
		for wordStructureToken in wordStructureTokens:
			wordStructureNode = wordStructureNodeClass(wordStructureToken, nodeType=nodeTypeWord, substructureSide=substructureSideNA, substructureLinkType=substructureLinkTypeNA)
			self.wordStructureNodes.append(wordStructureNode)
		
		#add wordStructure class to dictionary to enable fast lookup by word;
		wordStructureTokenFirst = wordStructureTokens[0]
		wordStructureTokenLast = wordStructureTokens[len(wordStructureTokens)-1]
		wordStructureClassDictionaryFirst[wordStructureTokenFirst].append(self)
		wordStructureClassDictionaryLast[wordStructureTokenLast].append(self)
	
def main():

	text_file = open("sentenceList.txt", "r")
	sentenceList = text_file.readlines()
	
	for sentence in sentenceList:
		sentenceTokens = word_tokenize(sentence)
		addSSESentence(sentenceTokens)

def addSSESentence(sentenceTokens):
	wordStructure = createSSE(sentenceTokens)
	addSSE(wordStructure, sentenceTokens)

def createSSE(sentenceTokens):
	print("addSSE = ", sentenceTokens)
	#see if sentence/wordStructure already exists in wordStructureDictionary
	resultFound, wordStructure = findWordStructure(sentenceTokens)
	if(not resultFound):
		wordStructure = wordStructureClass(sentenceTokens)
		#print(sentenceTokens)
	return wordStructure

def addSSE(wordStructure, sentenceTokens):
	SSEmatchStructure(wordStructure, sentenceTokens, SSEmatchSurroundStructure)
	SSEmatchStructure(wordStructure, sentenceTokens, SSEmatchFirstStructure)	#CHECKTHIS algorithm
	SSEmatchStructure(wordStructure, sentenceTokens, SSEmatchLastStructure)	#CHECKTHIS algorithm

	
def findWordStructure(sentenceTokens):	#CHECKTHIS; only supports wordStructure match by (wordStructureNodeType == nodeTypeWord)
	resultFound = False
	resultWordStructure = None
	wordStructureTokenFirst = sentenceTokens[0]
	wordStructureList = wordStructureClassDictionaryFirst[wordStructureTokenFirst]
	for wordStructure in wordStructureList:
		#if(wordStructure is not None):
		if(len(wordStructure.wordStructureNodes) == len(sentenceTokens)):
			#candidate matches require identical wordStructure lengths
			foundMatchedNode = True
			for wordStructureNodeIndex in range(len(sentenceTokens)):
				wordStructureNode = wordStructure.wordStructureNodes[wordStructureNodeIndex]
				for wordStructureNodeValue in wordStructureNode.possibleValues:
					#if(wordStructureNodeValue.nodeType == nodeTypeWord):	#CHECKTHIS
					if(wordStructureNodeValue.content != sentenceTokens[wordStructureNodeIndex]):
						foundMatchedNode = False
			if(foundMatchedNode):
				resultFound = True
				resultWordStructure = wordStructure
	return resultFound, resultWordStructure
	
#eg find "The red dog [MASKED OUT: near the house] is happy." in list["The red dog is happy.", "...", etc]
def SSEmatchStructure(wordStructure, sentenceTokens, SSEmatchStructureType):
	sentenceTokenIndexLast = len(sentenceTokens)-1
	if(SSEmatchStructureType == SSEmatchSurroundStructure):
		maskedTokenIndexFirst = 1
		maskedTokenIndexLast = sentenceTokenIndexLast-1
	elif(SSEmatchStructureType == SSEmatchFirstStructure):
		maskedTokenIndexFirst = 1
		maskedTokenIndexLast = sentenceTokenIndexLast
	elif(SSEmatchStructureType == SSEmatchLastStructure):
		maskedTokenIndexFirst = 0
		maskedTokenIndexLast = sentenceTokenIndexLast-1
	
	for maskedTokenIndexStart in range(maskedTokenIndexFirst, maskedTokenIndexLast+1):	#note last index is excluded from range
		for maskedTokenIndexEnd in range(maskedTokenIndexStart+1, maskedTokenIndexLast+1):
			
			sentenceTokensMask = sentenceTokens[maskedTokenIndexStart:maskedTokenIndexEnd]
			sentenceTokensMaskedPart1 = sentenceTokens[0:maskedTokenIndexStart]
			sentenceTokensMaskedPart2 = sentenceTokens[maskedTokenIndexEnd:sentenceTokenIndexLast+1]
			sentenceTokensMasked = sentenceTokensMaskedPart1 + sentenceTokensMaskedPart2
			sentenceTokensMaskedIndexLast = len(sentenceTokensMasked)-1
			
			resultFound, wordStructureMasked = findWordStructure(sentenceTokensMasked)
			print("\tsentenceTokensMasked = ", sentenceTokensMasked)
			if(resultFound):
				print("\tresultFound")
		
				wordStructureMask = createSSE(sentenceTokensMask)

				if(SSEmatchStructureType == SSEmatchSurroundStructure):
					wordStructureNodeDivergeIndex = maskedTokenIndexStart-1
					wordStructureNodeDiverge = wordStructureMasked.wordStructureNodes[wordStructureNodeDivergeIndex]
					wordStructureNodeValueNew = wordStructureNodeValueClass(wordStructureMask, nodeType=nodeTypeSubstructure, substructureSide=substructureSideRight, substructureLinkType=substructureLinkTypeInsertion)
					wordStructureNodeDiverge.possibleValues.append(wordStructureNodeValueNew)
					#optional: also add substructure to left of node2
					wordStructureNodeDivergeIndex = sentenceTokensMaskedIndexLast - (sentenceTokenIndexLast-maskedTokenIndexEnd)
					wordStructureNodeDiverge2 = wordStructureMasked.wordStructureNodes[wordStructureNodeDivergeIndex]
					wordStructureNodeValueNew2 = wordStructureNodeValueClass(wordStructureMask, nodeType=nodeTypeSubstructure, substructureSide=substructureSideLeft, substructureLinkType=substructureLinkTypeInsertion)
					wordStructureNodeDiverge2.possibleValues.append(wordStructureNodeValueNew2)
				elif(SSEmatchStructureType == SSEmatchFirstStructure):
					wordStructureNodeDivergeIndex = maskedTokenIndexStart-1
					wordStructureNodeDiverge = wordStructureMasked.wordStructureNodes[wordStructureNodeDivergeIndex]
					wordStructureNodeValueNew = wordStructureNodeValueClass(wordStructureMask, nodeType=nodeTypeSubstructure, substructureSide=substructureSideRight, substructureLinkType=substructureLinkTypeReplacement)
					wordStructureNodeDiverge.possibleValues.append(wordStructureNodeValueNew)
				elif(SSEmatchStructureType == SSEmatchLastStructure):
					wordStructureNodeDivergeIndex = sentenceTokensMaskedIndexLast - (sentenceTokenIndexLast-maskedTokenIndexEnd)	#or 0
					if(wordStructureNodeDivergeIndex != 0):
						print("error: (wordStructureNodeDivergeIndex != 0)")
						exit()
					wordStructureNodeDiverge = wordStructureMasked.wordStructureNodes[wordStructureNodeDivergeIndex]
					wordStructureNodeValueNew = wordStructureNodeValueClass(wordStructureMask, nodeType=nodeTypeSubstructure, substructureSide=substructureSideLeft, substructureLinkType=substructureLinkTypeReplacement)
					wordStructureNodeDiverge.possibleValues.append(wordStructureNodeValueNew)

				if(SSErecurse):
					addSSE(wordStructureMask, sentenceTokensMask)
			
if __name__ == '__main__':
	main()


