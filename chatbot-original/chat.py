import random
import json
import torch
from model import NeuralNet
from preprocessing import get_features, tokenize, replace_currencies

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as f:
	intents = json.load(f)

FILE = 'data.pth'
data = torch.load(FILE)

input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()


def get_response(sentence):
	sentence = sentence.lower()
	sentence = tokenize(sentence)
	sentence, convertion_dict = replace_currencies(sentence)
	x = get_features(sentence, all_words)
	x = x.reshape(1, x.shape[0])
	x = torch.from_numpy(x)

	output = model(x)
	_, predicted = torch.max(output, dim = 1)
	tag = tags[predicted.item()]
	probs = torch.softmax(output, dim = 1)
	prob = probs[0][predicted.item()]

	if prob.item() > 0.75:
		for intent in intents['intents']:
			if tag == intent['tag']:
				return format_response(random.choice(intent['responses']), convertion_dict)
	else:
		return format_response("I do not understand...", {})

def format_response(string, payload):
	for key in payload.keys():
		string = string.replace("{"+ key + "}", payload[key])
	return {
		"output": string,
		"payload": payload
	}


print(get_response(input()))

