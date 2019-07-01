#Submitted By Ashish Peruri(vperur2@uic.edu) and Srikanth Maganti(smagan20@uic.edu)

#----------------------------------------------------Code Begins Here ----------------------------------------------------------

import nltk
from nltk import CFG
from nltk.parse import CoreNLPParser
from nltk.parse import CoreNLPDependencyParser
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords


stop_words = set(stopwords.words('english')) # stopwords from nltk 
parser = CoreNLPParser(url='http://localhost:9000') # running a local server 
file = open("vperur2_smagan20.txt","w+") # output file containing all the the questions their categories and parsed trees
def findWords(question):
	"""
	Returns words other than stopwords
	"""
	tagsList = []
	tokens=nltk.word_tokenize(question)
	tagsList.append(nltk.pos_tag(tokens))
	wordsList=[]
	for tags in tagsList:
		for tag in tags:
			# Removing Punctuations and stop_words after pos_tagging
			if tag[0] not in """!()-[]{};:'",<>./@#?""" and tag[0].lower() not in stop_words:
				wordsList.append(tag[0])
	return wordsList

def findCategory(question):
	"""
	Finds The Category of a Question
	"""
	wordsList = findWords(question)
	categories = ['GEOGRAPHY','MUSIC','MOVIE']
	singerList1 = ['Beyonce','Gaga','Beyonce','Taylor Swift']
	singerList2 = ['Michael','Jackson']
	singerList3 = ['Swift', 'Taylor']
	#There are only 5 singers in the whole singer Table
	singerPresent = False
	bornPresent = 'born' in wordsList
	for i in singerList1:
		if i in wordsList:
			singerPresent = True
		if singerPresent and bornPresent:
			return 'MUSIC'
	for i in singerList2:
		if i in wordsList:
			singerPresent = True
		else:
			singerPresent = False
	if singerPresent and bornPresent:
		return 'MUSIC'
	for i in singerList3:
		if i in wordsList:
			singerPresent = True
		else:
			singerPresent = False
	if singerPresent and bornPresent:
		return 'MUSIC'
	#So if they are present with the word in there the categorization is done as Singer

	# words taken to increase similarity measures
	location = [wn.synsets('location')[0],wn.synsets('city')[0],wn.synsets('place')[0],wn.synsets('ocean')[0],wn.synsets('province')[0]]
	music = [wn.synsets('music')[0],wn.synsets('album')[0],wn.synsets('sing')[0],wn.synsets('pop')[0],wn.synsets('born')[0]]
	movie = [wn.synsets('actor')[0],wn.synsets('movie')[0],wn.synsets('star')[0],wn.synsets('oscar')[0],wn.synsets('born')[0]]
	s1,s2,s3 = 0,0,0
	for word in wordsList:
		li = wn.synsets(word)
		if li != []:
			for i in location:
				temp = wn.wup_similarity(li[0], i)
				if(temp!=None):
					if(temp == 1): #Reinforcing similarity
						s1 += 10*temp
					else:
						s1 += temp
			for i in music:
				temp = wn.wup_similarity(li[0], i)
				if(temp!=None):
					if(temp == 1): #Reinforcing similarity
						s2 += 10*temp
					else:
						s2 += temp
			for i in movie:
				temp = wn.wup_similarity(li[0], i)
				if(temp!=None):
					if(temp == 1): #Reinforcing similarity
						s3 += 10*temp
					else:
						s3 += temp
	cList = [s1,s2,s3]
	index = cList.index(max(cList))
	return categories[index] #Returns the category of the  question


if __name__ == '__main__':
	print("Please Input the File Path of the input file")
	print(r"The format is path\input.txt")
	path = str(input())
	inputFile = open(path,"r+")
	file.write("The parsed trees for the input are as follows\n")
	questionsList = inputFile.readlines()
	for question in questionsList:
		question = question.strip()
		if question!="":
			#finding category of question
			category = findCategory(question)
			file.write("<QUESTION> %s"%question)
			file.write("<CATEGORY> %s\n"%category)
			file.write("<PARSETREE>\n")
			l = list(next(parser.raw_parse(question)))
			file.writelines(["%s " %word for word in l])
			print("<QUESTION> %s"%question)
			print("<CATEGORY> %s"%category)
			print("<PARSETREE>")
			for word in l:
				print("%s " %word)


#------------------------------------------------------------Code Ends Here -----------------------------------------------------------------


