from preProcessing.inputData import readLines
from preProcessing.preProcessing import pre_process_final
from training.model_with_beam import create_model
from predictions.pred_with_beam import decode_sequence_beam
#from flask import Flask
#from keras import backend as K
#import tensorflow as tf
import numpy as np
import codecs
import pickle
import h5py



numSent = 1000000
trainSize = 800000

#Read sentences from files
lines = readLines(numSent)
print('Data read from files')

#Pre-process
# pre_proc_list = pre_process_final(lines, numSent)
# print('Saving clean data to pickle') 
# pickle.dump( pre_proc_list, open( "clean_data_1M.p", "wb" ) )
# print('Clean data saved') 

#Load clean data from pickle file
pre_proc_list = pickle.load( open( "clean_data.p", "rb" ) )
print('Clean data loaded from pickle')

maxLen = pre_proc_list[0]   #maximum lengths of sentences
tokens = pre_proc_list[1]   #get list of all tokens from pre-process

maxHindi = maxLen[0]
maxEng = maxLen[1]
print('Hindi Max: ', maxHindi)
print('Eng Max: ', maxEng)
print('********')
#print (clean_sentences[:5])

print('Cleaning done')
clean_sentences = tokens[0]
num_encoder_tokens = tokens[1] 
num_decoder_tokens = tokens[2] 
input_token_index = tokens[3] 
target_token_index = tokens[4]

train, test = clean_sentences[:trainSize] , clean_sentences[trainSize:]

#tf.keras.backend.clear_session()
print('Loading Model')
#Model
embedding_size = 50
modelList = create_model(train, test,
                        num_encoder_tokens,
                        num_decoder_tokens, 
                        maxHindi,
                        maxEng,
                        input_token_index,
                        target_token_index,
                        embedding_size, 
                        numSent)
                                 

model = modelList[0]
encoder_model = modelList[1]
encoder_input_data_train = modelList[2]
decoder_input_data_train = modelList[3]
decoder_target_data_train = modelList[4]
encoder_input_data_test = modelList[5]
decoder_input_data_test = modelList[6]
decoder_target_data_test = modelList[7]
decoder_model = modelList[8]
graph = modelList[9]

print ('Model loaded')


print('***************Making Sample Predictions*************\n')

def tokenize_input(input_sentence):
    input_sent = []
    for word in input_sentence.split(' '):
        input_sent.append(word)
    index_array = np.zeros((1, 30), dtype='float32')
    index = 0
    for item in input_sent:
        if item not in input_token_index:
            index_array[0, index] = 0.
        else:
            index_array[0, index] = input_token_index[item]
        index = index + 1
    return index_array
    
#@app.route('/translate/<input_from_user>')
def make_preds(input_from_user):
    print('Inside make_preds')
    print('input from user: ',input_from_user)
    #Training predictions
    input_sent_list = list()
    source_sent_list = list()
    target_sent_list = list()
    print('Starting predictions')
    input_from_user = open('hindi_input.txt', encoding='utf-8', errors='ignore').read()
    encoded_sent = tokenize_input(input_from_user)

    #Beam serach
    decoded_sentence_list = []
    #K.clear_session()
    with graph.as_default():
      states_value = encoder_model.predict(encoded_sent)
    target_seq = np.zeros((1,1))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0] = target_token_index['START_']
    stop_condition = False
    decoded_sentence = ''
    current_sent_prob = 1.0
    decode_sequence_beam(states_value, target_seq, decoded_sentence, decoded_sentence_list, stop_condition, 
                            current_sent_prob, decoder_model, input_token_index, target_token_index, graph)
    #print('*********Source************\n', input_from_user)
    sortedSent = sorted(decoded_sentence_list, key=lambda kv: kv[1], reverse=True)
    #print('*********Decoded sentence with Beam Search***********\n', sortedSent[:5])
    with open('eng_output.txt', 'w', errors='ignore') as opfile:
        opfile.write(sortedSent[0][0])
    