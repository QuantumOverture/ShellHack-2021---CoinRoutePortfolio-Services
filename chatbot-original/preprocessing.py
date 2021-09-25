import json
import nltk
#nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
import numpy as np


def tokenize(sentence):
	return nltk.word_tokenize(sentence)

def stem(word):
	stemmer = PorterStemmer()
	return stemmer.stem(word.lower())

def replace_currencies(tokenized_sentence):
	equality_dict = {}
	with open('./equality.json', 'r') as f:
		equality_dict = json.load(f)
	equality_dict_lower = equality_dict
	all_currencies = []
	for key in equality_dict:
		for index, item in enumerate(equality_dict[key]):
			all_currencies.append(item.lower())
			equality_dict_lower[key][index] = item.lower()

	updated_currency_count = 1
	convertion_dict = {}
	updated_tokenized_sentence = []
	for w in tokenized_sentence:
		if w in all_currencies:
			for key in equality_dict:
				if w in equality_dict_lower[key]:
					convertion_dict["CURRENCY_" + str(updated_currency_count) + "_NAME"] = equality_dict[key][0]
					updated_tokenized_sentence.append("{CURRENCY_" + str(updated_currency_count) + "_NAME}")
					updated_currency_count += 1
		else:
			updated_tokenized_sentence.append(w)

	return updated_tokenized_sentence, convertion_dict


def get_features(tokenized_sentence, all_words):
	tokenized_sentence = [stem(w) for w in tokenized_sentence]
	bag = np.zeros(len(all_words), dtype = np.float32)
	for idx, w in enumerate(all_words):
		if w in tokenized_sentence:
			bag[idx] = 1.0
	return bag
	

