from keras.layers import Input, LSTM, Embedding, Dense
from keras.models import Model
from keras.utils import plot_model
import tensorflow as tf
from math import log
from numpy import array
from numpy import argmax
import numpy as np

def reverse_mapping(input_token_index, target_token_index):

    # Reverse-lookup token index to decode sequences back to
    # something readable.
    reverse_input_char_index = dict(
        (i, char) for char, i in input_token_index.items())
    reverse_target_char_index = dict(
        (i, char) for char, i in target_token_index.items())

    return (reverse_input_char_index, reverse_target_char_index)
    
    
#Beam Search
def beam_search(data, k, input_token_index, target_token_index):

    rev_map = reverse_mapping(input_token_index, target_token_index)
    reverse_input_char_index = rev_map[0]
    reverse_target_char_index = rev_map[1]

    sequences = [[list(), 1.0]]
    # walk over each step in sequence
    #for row in data:
    all_candidates = list()
    # expand each current candidate
    for i in range(len(sequences)):
        seq, score = sequences[i]
        for j in range(len(data)):
            candidate = [seq + [j], score * - np.log(data[j])]
            all_candidates.append(candidate)
    # order all candidates by score
    ordered = sorted(all_candidates, key=lambda tup:tup[1])
    # select k best
    sequences = np.array(ordered[:k])
    word1 = reverse_target_char_index[sequences[0,0][0]]
    word2 = reverse_target_char_index[sequences[1,0][0]]
    prob1 = data[sequences[0,0][0]]
    prob2 = data[sequences[1,0][0]]
    return [(word1, prob1, sequences[0,0][0]) , (word2, prob2, sequences[1,0][0])]


#Decode with Beam Search
def decode_sequence_beam(states_value, target_seq, decoded_sentence, decoded_sentence_list, stop_condition, current_sent_prob, decoder_model, input_token_index, target_token_index, graph):   
    if stop_condition == True:
        decoded_sentence_list.append((decoded_sentence, current_sent_prob))
        return
    #Else
    with graph.as_default():
      output_tokens, h, c = decoder_model.predict([target_seq] + states_value)  
    #print('output tokens shape: ', output_tokens.shape)
    sampled_tokens = beam_search(output_tokens[0, -1, :], 2, input_token_index, target_token_index)
    sampled_charA = sampled_tokens[0][0]
    sampled_charB = sampled_tokens[1][0]
    
    probA = sampled_tokens[0][1]
    probB = sampled_tokens[1][1]
    
    sampled_token_indexA = sampled_tokens[0][2]
    sampled_token_indexB = sampled_tokens[1][2]
    
#     print('Words: ', sampled_charA, sampled_charB)
#     print('Probabilities: ', probA, probB)

    if (sampled_charA == '_END' or len(decoded_sentence) > 52):
        #print('Decoded sentence after Beam: ', decoded_sentence)
        return decode_sequence_beam(states_value, target_seq, decoded_sentence, decoded_sentence_list, True, current_sent_prob, decoder_model, input_token_index, target_token_index, graph)
    if (sampled_charB == '_END' or len(decoded_sentence) > 52):
        #print('Decoded sentence after Beam: ', decoded_sentence)
        return decode_sequence_beam(states_value, target_seq, decoded_sentence, decoded_sentence_list, True, current_sent_prob, decoder_model, input_token_index, target_token_index, graph)
    decoded_sentenceA = decoded_sentence+' '+sampled_charA
    decoded_sentenceB = decoded_sentence+' '+sampled_charB
    target_seqA = np.zeros((1,1))
    target_seqB = np.zeros((1,1))
    target_seqA[0, 0] = sampled_token_indexA
    target_seqB[0, 0] = sampled_token_indexB
    # Update states
    states_value = [h, c]
    decode_sequence_beam(states_value, target_seqA, decoded_sentenceA, decoded_sentence_list, stop_condition, current_sent_prob * probA, decoder_model, input_token_index, target_token_index, graph)
    decode_sequence_beam(states_value, target_seqB, decoded_sentenceB, decoded_sentence_list, stop_condition, current_sent_prob * probB, decoder_model, input_token_index, target_token_index, graph)


#Decode without Beam
def decode_sequence(input_seq_list, embedding_size, input_token_index, target_token_index, dex, decoder_lstm, decoder_dense, encoder_model):

    rev_map = reverse_mapping(input_token_index, target_token_index)
    
    reverse_input_char_index = rev_map[0]
    reverse_target_char_index = rev_map[1]
    
    decoded_sentence_list = []
    
    for input_seq in input_seq_list:
      # Encode the input as state vectors.
      states_value = encoder_model.predict(input_seq)
      # Generate empty target sequence of length 1.
      target_seq = np.zeros((1,1))
      # Populate the first character of target sequence with the start character.
      target_seq[0, 0] = target_token_index['START_']
  
      # Sampling loop for a batch of sequences
      # (to simplify, here we assume a batch of size 1).
      stop_condition = False
      decoded_sentence = ''
      while not stop_condition:
          output_tokens, h, c = decoder_model.predict(
              [target_seq] + states_value)
  
          # Sample a token
          sampled_token_index = np.argmax(output_tokens[0, -1, :])
          sampled_char = reverse_target_char_index[sampled_token_index]
          decoded_sentence += ' '+sampled_char
  
          # Exit condition: either hit max length
          # or find stop character.
          if (sampled_char == '_END' or
             len(decoded_sentence) > (embedding_size+2)):
              stop_condition = True
  
          # Update the target sequence (of length 1).
          target_seq = np.zeros((1,1))
          target_seq[0, 0] = sampled_token_index
  
          # Update states
          states_value = [h, c]
      decoded_sentence_list.append(decoded_sentence)

    return decoded_sentence_list