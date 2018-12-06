from keras.layers import Input, LSTM, Embedding, Dense
from keras.models import Model
from keras.utils import plot_model
import tensorflow as tf
import numpy as np

def reverse_mapping(embedding_size, input_token_index, target_token_index, dex, decoder_lstm, decoder_dense):

    decoder_inputs = Input(shape=(None,))  ##Already done in create_model()
    decoder_state_input_h = Input(shape=(embedding_size,))
    decoder_state_input_c = Input(shape=(embedding_size,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

    final_dex2= dex(decoder_inputs)

    decoder_outputs2, state_h2, state_c2 = decoder_lstm(final_dex2, initial_state=decoder_states_inputs)
    decoder_states2 = [state_h2, state_c2]
    decoder_outputs2 = decoder_dense(decoder_outputs2)
    decoder_model = Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs2] + decoder_states2)

    # Reverse-lookup token index to decode sequences back to
    # something readable.
    reverse_input_char_index = dict(
        (i, char) for char, i in input_token_index.items())
    reverse_target_char_index = dict(
        (i, char) for char, i in target_token_index.items())

    return (decoder_model, reverse_input_char_index, reverse_target_char_index)

#def decode_sequence(input_seq, embedding_size, input_token_index, target_token_index, decoder_inputs, dex):
def decode_sequence(input_seq_list, embedding_size, input_token_index, target_token_index, dex, decoder_lstm, decoder_dense, encoder_model):

    decoder_model_list = reverse_mapping(embedding_size, input_token_index, target_token_index, dex, decoder_lstm, decoder_dense)
    
    decoder_model = decoder_model_list[0]
    reverse_input_char_index = decoder_model_list[1]
    reverse_target_char_index = decoder_model_list[2]
    
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