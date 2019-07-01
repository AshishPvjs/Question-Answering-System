import pprint
import string
import sqlite3
import nltk
from nltk.parse import CoreNLPParser
from nltk.parse import CoreNLPDependencyParser
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk import load_parser
from nltk.tree import *
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn


qcount = 1
musicDBConn = sqlite3.connect('music.sqlite')
geographyDBConn = sqlite3.connect('WorldGeography.sqlite')
movieDBConn = sqlite3.connect('oscar-movie_imdb.sqlite')
musicDB = musicDBConn.cursor()
geographyDB = geographyDBConn.cursor()
movieDB = movieDBConn.cursor()

pos_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='pos')
nerTagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
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
	mList = ['Titanic']
	#There are only 5 singers in the whole singer Table
	for i in wordsList:
		if i in mList:
			return 'MOVIE'
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
	location = [wn.synsets('location')[0],wn.synsets('city')[0],wn.synsets('place')[0],wn.synsets('ocean')[0],wn.synsets('province')[0],wn.synsets('state')[0]]
	music = [wn.synsets('music')[0],wn.synsets('album')[0],wn.synsets('sing')[0],wn.synsets('pop')[0],wn.synsets('born')[0],wn.synsets('track')[0]]
	movie = [wn.synsets('actor')[0],wn.synsets('movie')[0],wn.synsets('star')[0],wn.synsets('oscar')[0],wn.synsets('born')[0],wn.synsets('directed')[0]]
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




def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)


def createGrammar(query,category):
	parsetree = list(parser.raw_parse(query))
	# Tree.fromstring(str(parsetree[0])).pretty_print()
	t = Tree.fromstring(str(parsetree[0]))
	productions = Tree.productions(t)
	count = 0
	nnpcount = 0
	whnpcount  = 0
	jjscount = 0
	wincount = 0
	woncount = 0
	oscarcount = 0
	bestcount = 0
	whichcount = 0
	whencount = 0
	moviecount = 0
	whatcount = 0
	wherecount = 0
	for i in productions:
		s = str(i)
		tempRuleList = s.split('->')
		tls = tempRuleList[1].split()
		if("NNP" in tls):
			nnpcount += 1
		if("WHNP" in tls):
			whnpcount+=1
		if("JJS" in tls):
			jjscount+=1
		if("'won'" in tls):
			woncount+=1
		if("'win'" in tls):
			wincount+=1
		if("'oscar'" in tls):
			oscarcount+=1
		if("'best'" in tls):
			bestcount+=1
		if("'movie'" in tls):
			moviecount+=1
		if("'Which'" in tls):
			whichcount += 1
		if("'When'" in tls):
			whencount += 1
		if("'What'" in tls):
			whatcount += 1
		if("'Where'" in tls):
			wherecount += 1
	cfgRHSList = []
	cfgLHSList = []
	wordsList = query.split()
	stopwords = ["'Is'","'Was'","'Did'","'Who'","'Which'","'When'","'a'","'an'","'the'","'in'","'on'","'with'","'best'","'for'","'oscar'"]
	rulesList = ["'director'","'actor'"]
	stopwords1 = ["'Is'","'Was'","'Did'","'Who'","'Which'","'Does'","'When'","'a'","'an'","'the'","'in'","'on'","'with'","'for'","'oscar'"]
	stopwords2 = ["'Is'","'Was'","'Did'","'Who'","'Which'","'When'","'Does'","'album'","'track'","'Genre'","'Artist'","'Where'","'was'","'a'","'an'","'the'","'on'","'with'","'for'","'oscar'","'by'","'in'"]
	stopwords3 = ["'Is'","'Was'","'Did'","'Who'","'Which'","'When'","'What'","'Does'","'Where'","'a'","'an'","'the'","'on'","'with'","'for'","'oscar'","'by'","'is'","'of'"]
	if wordsList[0] in ["Did","Was"] and category=='MUSIC':
		for i in productions:
			s = str(i)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if k=="NP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select count(*) \""+"+"
							count +=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						print(k)
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords2:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if(tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'sing'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Artist A inner join Album AL on A.id = AL.artsitId inner join Track T on AL.albumID = T.albumID where A.name like \'%{"+"}%\' and T.name like \'%{"+"}%\' . \""+"]"
					elif(tempRuleList[0].strip() == "VBN" and tempRuleList[1].strip() == "'born'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Artist A where A.name like \'%{"+"}%\' and A.placeofBith like \'%{"+"}%\' . \""+"]"
					else:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	elif wordsList[0] in ["Does"] and category=='MUSIC':
		for i in productions:
			s = str(i)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if k=="NP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select count(*) \""+"+"
							count +=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords2:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if(tempRuleList[0].strip() == "VBP" and tempRuleList[1].strip() == "'include'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Album AL inner join Track T on AL.albumID = T.albumId  where AL.name like \'%{"+"}%\' and T.name like \'%{"+"}%\' . \""+"]"
					else:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	elif wordsList[0] in ["Where"] and category=='MUSIC':
		for i in productions:
			s = str(i)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if k=="NP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select A.placeofBith from Artist A where A.name like \'%{"+"}%\' . \""+"+"
							count +=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords2:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				elif(tempRuleList[0].strip() == "VBN" and tempRuleList[1].strip() == "'born'"):
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='']"
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	elif wordsList[0] in ["Is","Was"] and category =='GEOGRAPHY':
		for i in productions:
			s = str(i)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if k=="NP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select count(*) \""+"+"
							count +=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords3:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if(tempRuleList[0].strip() == "IN" and tempRuleList[1].strip() == "'in'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Countries CY inner join CountryContinents CC on CY.id = CC.CountryId inner join Continents CO on CC.ContinentId = CO.id where CY.name like \'%{"+"}%\' and CO.continent like \'%{"+"}%\' . \""+"]"
					elif(tempRuleList[0].strip() == "NN" and tempRuleList[1].strip() == "'capital'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Cities CI inner join Capitals CA on CI.id = CA.CityId inner join Countries CY on CA.CountryId = CY.id where CI.name like \'%{"+"}%\' and CY.name like \'%{"+"}%\' . \""	+"]"
					else:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	elif wordsList[0] in ["What","Where"] and category =='GEOGRAPHY':
		for i in productions:
			s = str(i)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			tempS = ""
			if nnpcount == 1:
				tempS = "from Countries CY inner join Capitals CA on CY.id = CA.CountryId inner join Cities CI ON CA.CityId = CI.id where CI.name like \'%{"+"}%\' . \""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if k=="WHNP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select CI.name \""+"+"
							count +=1
						elif k=="WHADVP" and count == 0 and wherecount>0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select CY.name " + tempS + "+"
							count +=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords3:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if(tempRuleList[0].strip() == "NN" and tempRuleList[1].strip() == "'capital'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Cities CI inner join Capitals CA on CI.id = CA.CityId inner join Countries CY on CA.CountryId = CY.id where CY.name like \'%{"+"}%\' . \""	+"]"
					elif(tempRuleList[0].strip() == "NN" and tempRuleList[1].strip() == "'is'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Cities CI inner join Capitals CA on CI.id = CA.CityId inner join Countries CY on CA.CountryId = CY.id where CY.name like \'%{"+"}%\' . \""	+"]"
					else:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)

	elif wordsList[0] in ["Is","Was"] and category =='MOVIE':
		for i in productions:
			s = str(i)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if k=="NP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select count(*) \""+"+"
							count +=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if tempRuleList[1].strip() == "'movie'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
					if tempRuleList[0].strip()=="NN" and tempRuleList[1].strip() in ["'director'","'actor'"]:
						if tempRuleList[1].strip() == "'director'":
							# print("yes")
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join director D on P.id = D.director_id where P.name like \'%{"+"}%\' . \"" + "]"
						if tempRuleList[1].strip() == "'actor'":
							# print("yes")
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join actor A on P.id = A.actor_id where P.name like \'%{"+"}%\' . \"" + "]"
					elif(tempRuleList[0].strip() == "IN" and tempRuleList[1].strip() == "'by'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join director D on P.id = D.director_id inner join movie M on D.movie_id = M.id where M.name like \'%{"+"}%\' and P.name like \'%{"+"}%\' . \""+"]"
					elif(tempRuleList[0].strip() == "VBN" and tempRuleList[1].strip() == "'born'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P where P.name like \'%{"+"}%\' and P.pob like \'%{"+"}%\' . \""	+"]"
					elif(tempRuleList[0].strip() == "JJS" and tempRuleList[1].strip() == "'best'"):
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Movie M inner join oscar O on M.id = O.movie_id where M.name like \'%{"+"}%\' and O.year like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[1].strip() != "'movie'":
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	elif wordsList[0] == "Did" and category =='MOVIE':
		# print('yay')
		for i in productions:
			s = str(i)
			# print(s)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						if(k=="NP" and count == 0):
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select count(*) \""+"+"
							count +=1
						elif(k=="S" and wincount>0 and oscarcount>0 and bestcount>0):
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select count(*) \""+"+"
							count+=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if tempRuleList[0].strip()=="JJ" and tempRuleList[1].strip() in ["'Italian'","'American'","'British'","'French'","'German'"]:
						if tempRuleList[1].strip() == "'Italian'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='Italy"+"']"
						elif tempRuleList[1].strip() == "'American'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='USA"+"']"
						elif tempRuleList[1].strip() == "'British'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='UK"+"']"
						elif tempRuleList[1].strip() == "'French'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='France"+"']"
						elif tempRuleList[1].strip() == "'German'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='Germany"+"']"
					elif tempRuleList[0].strip() == "NN" and tempRuleList[1].strip() in ["'film'","'movie'"]:
						if tempRuleList[1].strip() == "'film'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='picture"+"']"
						elif tempRuleList[1].strip() == "'movie'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
					elif tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'star'":
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Actor A on P.id = A.actor_id inner join movie M on A.actor_id = M.id where P.name like \'%{"+"}%\' and M.name like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'direct'":
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join director D on P.id = D.director_id inner join Movie M on D.movie_id = M.id where P.name like \'%{"+"}%\' and M.name like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'win'" and oscarcount>0 and bestcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Director D on P.id = D.director_id inner join oscar O on D.movie_id = O.movie_id where P.name like \'%{"+"}%\' and O.type like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'win'" and nnpcount > 0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join oscar O on P.id = O.person_id where P.name like \'%{"+"}%\' and O.year like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'win'" and nnpcount == 0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join oscar O on P.id = O.person_id where P.pob like \'%{"+"}%\' and O.type like \'%{"+"}%\' and O.year like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBP" and tempRuleList[1].strip() == "'win'" and oscarcount>0 and bestcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Director D on P.id = D.director_id inner join oscar O on D.movie_id = O.movie_id where P.name like \'%{"+"}%\' and O.type like \'%{"+"}%\' . \""+"]"
					else:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	elif wordsList[0] in ["Who","Which","When"] and category =='MOVIE':
		# print('yay')
		for i in productions:
			s = str(i)
			# print(s)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					# print("Hello")
					# print(tempRuleList[1].split())
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					# print("Yello")
					# print(tempRuleList[1])
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				# print(lhslist)
				lhsRuleSet = set(lhslist)
				# print(lhsRuleSet)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						# print(k)
						if k=="WHNP" and whichcount>0 and moviecount>0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select M.name \""+"+"
						elif k=="WHADVP" and count == 0 and whencount>0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select O.year \""+"+"
							count +=1
						elif k=="WHNP" and count == 0:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"+"\"select P.name \""+"+"
							count+=1
						else:
							lhsRuleDict[k]+=1
							rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						# k = k.translate(str.maketrans('', '', string.punctuation))
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords:
					# print(tempRuleList[1].strip())
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					if tempRuleList[0].strip()=="JJ" and tempRuleList[1].strip() in ["'Italian'","'American'","'British'","'French'","'German'"]:
						# print(tempRuleList[1].strip())
						if tempRuleList[1].strip() == "'Italian'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='Italy"+"']"
						if tempRuleList[1].strip() == "'American'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='USA"+"']"
						if tempRuleList[1].strip() == "'British'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='UK"+"']"
						if tempRuleList[1].strip() == "'French'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='France"+"']"
						if tempRuleList[1].strip() == "'German'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='Germany"+"']"
					elif tempRuleList[0].strip()=="NN" and tempRuleList[1].strip() in ["'movie'"]:
						if tempRuleList[1].strip() == "'movie'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='picture"+"']"
					elif tempRuleList[0].strip()=="NN" and tempRuleList[1].strip() in ["'actor'","'supporting-actor'","'actress'","'supporting-actress'"]:
						if tempRuleList[1].strip() == "'actor'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='best-actor"+"']"
						if tempRuleList[1].strip() == "'supporting-actor'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='best-supporting-actor"+"']"
						if tempRuleList[1].strip() == "'actress'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='best-actress"+"']"
						if tempRuleList[1].strip() == "'supporting-actress'":
							rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='best-supporting-actress"+"']"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'directed'" and bestcount==0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Director D on P.id = D.director_id inner join movie M on D.movie_id = M.id where M.name like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'acted'" and bestcount==0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Actor A on P.id = A.actor_id inner join movie M on A.movie_id = M.id where M.name like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'won'" and woncount>0 and oscarcount>0 and bestcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join oscar O on P.id = O.person_id where O.year like  \'%{"+"}%\' and  O.type like  \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'directed'" and bestcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Director D on P.id = D.director_id inner join Oscar O on D.movie_id = O.movie_id where O.year like \'%{"+"}%\' and O.type like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'acted'" and bestcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Actor A on P.id = A.actor_id inner join Oscar O on A.movie_id = O.movie_id where O.year like \'%{"+"}%\' and O.type like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'won'" and moviecount==0 and whichcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from person P inner join Oscar O on P.id = O.person_id where P.pob like \'%{"+"}%\' and O.type like \'%{"+"}%\' and O.year like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'won'" and moviecount>0 and whichcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Movie M inner join Oscar O on M.id = O.person_id where O.type like \'%{"+"}%\' and O.year like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'won'" and moviecount>0 and whichcount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Movie M inner join Oscar O on M.id = O.person_id where O.type like \'%{"+"}%\' and O.year like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VBD" and tempRuleList[1].strip() == "'did'" and whencount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + "\"from Oscar O inner join person P on O.person_id = P.id where O.type like \'%{"+"}%\' and P.name like \'%{"+"}%\' . \""+"]"
					elif tempRuleList[0].strip() == "VB" and tempRuleList[1].strip() == "'win'" and whencount>0:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='']"
					else:
						rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	else:
		for i in productions:
			s = str(i)
			# print(s)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				lhsRuleSet = set(lhslist)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
def returnBlocks(query):
	qlist = query.split()
	a,b,c = 0,1,1
	t1,t2,t3 = [],[],[]
	for i in qlist:
		if i != "FROM" and a == 0:
			t1.append(i)
		elif i == "FROM":
			a = 1
			b = 0
		if i != "WHERE" and b == 0:
			t2.append(i)
		elif i == "WHERE":
			b = 1
			c = 0
		if c==0:
			t3.append(i)
	s1 = ' '.join(t1)
	s2 = ' '.join(t2)
	s3 = ' '.join(t3)
	print(s1)
	print(s2)
	print(s3)
	return (s1,s2,s3)


def createQuery(query,category,qcount):
	finalquery = query
	if(category == 'MOVIE'):
		personName,movieName =[],[]
		pos_tags=list(pos_tagger.tag(query.split()))
		pos_tags.append(('last','$$$'))
		nnpTags,year = [],0
		for i,k in enumerate(pos_tags):
			if pos_tags[i+1][1] == '$$$':
				break
			elif pos_tags[i][1]=='NNP' and pos_tags[i+1][1]!='NNP':
				nnpTags.append(pos_tags[i][0])
			elif pos_tags[i][1]=='NNP' and pos_tags[i+1][1]=='NNP':
				nnpTags.append(pos_tags[i+1][0])
			if pos_tags[i][1]=='CD':
				year=pos_tags[i][0]
		for i in nnpTags:
			temporaryqueryperson=("select name from person where name like '%{}%'").format(i)
			temporaryquerymovie=("select name from movie where name like '%{}%'").format(i)
			# print(temporaryqueryperson)
			# print(temporaryquerymovie)
			MovieT1=movieDBConn.execute(temporaryqueryperson.upper())
			for row in MovieT1:
					personName.append([row[0],0])
			MovieT2=movieDBConn.execute(temporaryquerymovie.upper())
			for row in MovieT2:
					movieName.append([row[0],0])
		for i in nnpTags:
			for k,x in enumerate(movieName):
				if (x[0].find(i))>=0:
					x[1]=x[1]+10
				else:
					x[1]=x[1]-1
			for j,y in enumerate(personName):
				if (y[0].find(i))>=0:
					y[1]=y[1]+10
				else:
					y[1]=y[1]-1
		finalmovienames,finalpersonnames,filteredmovienames=[],[],[]
		for i in personName:
			if i[1]>0:
				finalpersonnames.append(i[0])
		for i in movieName:
			if i[1]>0:
				finalmovienames.append(i[0])
		for i in finalmovienames:
			if i.find(':')>=0:
				filteredmovienames.append(i.split(':')[0])
			else:
				filteredmovienames.append(i)

		if (finalpersonnames!=[]) and (filteredmovienames!=[]):
			for i in finalpersonnames:
				for k in nnpTags:
					if i.find(k)>=0:
						PersonName=k
						newquery=query.replace(k,'PersonName')
						break
			for j in filteredmovienames:
				for l in nnpTags:
					if j.find(l)>=0:
						MovieName=j
						finalquery=newquery.replace(j,'MovieName')
		elif (finalpersonnames!=[]) and (filteredmovienames==[]):
			for i in finalpersonnames:
				for k in nnpTags:
					if i.find(k)>=0:
						PersonName=k
						finalquery=query.replace(k,'PersonName')
						break
		elif (finalpersonnames==[]) and (filteredmovienames!=[]):
			for j in filteredmovienames:
				for l in nnpTags:
					if j.find(l)>=0:
						MovieName=j
						finalquery=query.replace(j,'MovieName')
		# print(finalquery)
		nerList = list(nerTagger.tag((finalquery.split())))
		for i in nerList:
			if i[1] == "DATE":
				year = i[0]
				finalquery = finalquery.replace(year,"year")
			if i[1] in ["CITY","STATE OR PROVINCE","LOCATION","COUNTRY"]:
				location = i[0]
				finalquery =finalquery.replace(location,"location")
	elif category=='MUSIC':
		MusicT = musicDBConn.execute(''' SELECT name from album ''')
		for row in MusicT:
		    if row[0] in query:
		        query=query.replace(row[0],"AlbumName")
		        AlbumName=row[0]
		        # print(AlbumName,row[0])
		MusicT = musicDBConn.execute(''' SELECT name from artist ''')
		for row in MusicT:
		    if row[0] in query:
		        query=query.replace(row[0],"ArtistName")
		        ArtistName=row[0]
		MusicT = musicDBConn.execute(''' SELECT name from genres ''')
		for row in MusicT:
		    if row[0] in query:
		        query=query.replace(row[0],"GenreName")
		        GenreName=row[0]
		    
		MusicT = musicDBConn.execute(''' SELECT name from track ''')
		for row in MusicT:
		    if row[0] in query:
		        query=query.replace(row[0],"TrackName")
		        TrackName=row[0]
		finalquery = query
	else:
		geographyT = geographyDBConn.execute(''' SELECT name from cities ''')
		for row in geographyT:
		    if row[0] in query:
		        query=query.replace(row[0],"CityName")
		        CityName=row[0]
		        # print(AlbumName,row[0])
		geographyT = geographyDBConn.execute(''' SELECT name from countries ''')
		for row in geographyT:
		    if row[0] in query:
		        query=query.replace(row[0],"CountryName")
		        CountryName=row[0]
		finalquery=query
	filename = "newGrammar"+str(qcount)+".fcfg"
	grammarFile = open(filename,"w+")
	qcount+=1
	start,grammar = createGrammar(finalquery,category)
	grammarFile.write("%"+" start "+start+"\n")
	grammarFile.write(grammar)
	grammarFile.close()
	cp = load_parser(filename,trace=3)
	# print(finalquery)
	trees = list(cp.parse(finalquery.strip('?').split()))
	answer = trees[0].label()['SEM']
	answer = [s for s in answer if s]
	print(answer)
	q = ' '.join(answer)
	insertlambda=q
	templist=[]
	tlist = list(insertlambda.split(' '))
	for words in tlist:
		if words!="select":
			# print(1)
			templist.append(words)
		else:
			break
	temp = insertlambda
	reverselist = tlist[::-1]
	for words in reverselist:
		if words!= ".":
			templist.append(words)
		else:
			break
	initial,end = None,None
	tempstring = insertlambda.format(*templist)
	temporarystring=tempstring.split()
	for i,k in enumerate(temporarystring):
		if k=="select":
			initial=i
		if k==".":
			end=i
	if initial==None or end == None:
		return "Grammar Not Found"
	finalstring=' '.join(temporarystring[initial:end])
	tlist = (finalstring.strip()).split()
	if "'%PersonName%'" in tlist:
		PersonName = "\"%"+PersonName+"%\""
		tlist[tlist.index("'%PersonName%'")] = PersonName
	if "'%MovieName%'" in tlist:
		MovieName = "\"%"+MovieName+"%\""
		tlist[tlist.index("'%MovieName%'")] = MovieName
	if "'%location%'" in tlist:
		location = "\"%"+location+"%\""
		tlist[tlist.index("'%location%'")] = location
	if "'%year%'" in tlist:
		year = "\"%"+year+"%\""
		tlist[tlist.index("'%year%'")] = year
	if "'%ArtistName%'" in tlist:
		ArtistName = "\"%"+ArtistName+"%\""
		tlist[tlist.index("'%ArtistName%'")] = ArtistName
	if "'%AlbumName%'" in tlist:
		AlbumName = "\"%"+AlbumName+"%\""
		tlist[tlist.index("'%AlbumName%'")] = AlbumName
	if "'%GenreName%'" in tlist:
		GenreName = "\"%"+GenreName+"%\""
		tlist[tlist.index("'%GenreName%'")] = GenreName
	if "'%TrackName%'" in tlist:
		TrackName = "\"%"+TrackName+"%\""
		tlist[tlist.index("'%TrackName%'")] = TrackName
	if "'%CityName%'" in tlist:
		CityName = "\"%"+CityName+"%\""
		tlist[tlist.index("'%CityName%'")] = CityName
	if "'%CountryName%'" in tlist:
		CountryName = "\"%"+CountryName+"%\""
		tlist[tlist.index("'%CountryName%'")] = CountryName
	finalstring = ' '.join(tlist)
	finalstring =finalstring.upper()
	return finalstring
	


def executeQuery(query,category):
	if(category=='MOVIE'):
		DBConn = movieDBConn
	elif(category=='MUSIC'):
		DBConn = musicDBConn
	elif(category=='GEOGRAPHY'):
		DBConn = geographyDBConn
	try:
		TempT = DBConn.execute(query.upper())
	except Exception as err:
		return "I don't know the answer"
	ansList = []
	for i in TempT:
		ansList.append(i[0])
	if len(ansList) == 0:
		return "None"
	if(type(ansList[0])==type(1)):
		if ansList[0]>1000:
			return ansList[0]
		elif ansList[0]>=1:
			return "Yes"
		elif ansList[0] == 0:
			return "No"
	elif hasNumbers(ansList[0]) == False:
		return ansList[0]
	else:
		return "I don't know the answer"




if __name__ == '__main__':
	qcount = 1
	print("Please Input the File Path of the input file")
	print(r"The format is path\input.txt")
	path = str(input())
	inputFile = open(path,"r+")
	file.write("The parsed trees for the input are as follows\n")
	questionsList = inputFile.readlines()
	for question in questionsList:
		question = question.strip()
		if question!="":
				category = findCategory(question)
				file.write("<QUESTION> %s\n"%question)
				file.write("<QUERY>\n")
				query = createQuery(question,category,qcount)
				qcount+=1
				Select,From,Where=returnBlocks(query)
				answer = executeQuery(query,category)
				file.write("%s\n"%Select)
				file.write("%s\n"%From)
				file.write("%s\n"%Where)
				file.write("<ANSWER>  ")
				file.write("%s \n\n"%answer)
				print("<QUESTION> %s"%question)
				print("<QUERY>")
				print(Select)
				print(From)
				print(Where)
				print("<ANSWER>")
				print("%s\n"%answer)
	musicDB.close()
	geographyDB.close()
	movieDB.close()
