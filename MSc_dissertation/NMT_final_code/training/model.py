import pandas as pd
import numpy as np
from keras.layers import Input, LSTM, Embedding, Dense, Bidirectional
from keras.models import Model
from keras.utils import plot_model
import tensorflow as tf


def create_encoder_decoder(sentFrame, 
                            num_encoder_tokens,
                            num_decoder_tokens, 
                            maxHindi, 
                            maxEng, 
                            input_token_index, 
                            target_token_index):

    encoder_input_data = np.zeros((len(sentFrame.hindi), maxHindi), dtype='float32')
    decoder_input_data = np.zeros((len(sentFrame.eng), maxEng), dtype='float32')
    decoder_target_data = np.zeros((len(sentFrame.eng), maxEng, num_decoder_tokens), dtype='float32')

    for i, (input_text, target_text) in enumerate(zip(sentFrame.hindi, sentFrame.eng)):
       
        for t, word in enumerate(input_text.split()):
            encoder_input_data[i, t] = input_token_index[word]
        
        for t, word in enumerate(target_text.split()):
            # decoder_target_data is ahead of decoder_input_data by one timestep
            decoder_input_data[i, t] = target_token_index[word]
            if t > 0:
                # decoder_target_data will be ahead by one timestep and will not include the start character
                decoder_target_data[i, t - 1, target_token_index[word]] = 1.
    
    return (encoder_input_data , decoder_input_data, decoder_target_data)


def create_model(train, test, 
                num_encoder_tokens,
                num_decoder_tokens, 
                maxHindi, 
                maxEng,
                input_token_index, 
                target_token_index, 
                embedding_size, 
                numSent):

    #create encoder and decoder for training set
    enc_dec_data_train = create_encoder_decoder(train,
                                            num_encoder_tokens,
                                            num_decoder_tokens, 
                                            maxHindi, 
                                            maxEng, 
                                            input_token_index, 
                                            target_token_index)
    encoder_input_data_train = enc_dec_data_train[0]
    decoder_input_data_train = enc_dec_data_train[1]
    decoder_target_data_train = enc_dec_data_train[2]
    
    
    #create encoder and decoder for test set
    enc_dec_data_test = create_encoder_decoder(test,
                                            num_encoder_tokens,
                                            num_decoder_tokens, 
                                            maxHindi, 
                                            maxEng, 
                                            input_token_index, 
                                            target_token_index)
    encoder_input_data_test = enc_dec_data_test[0]
    decoder_input_data_test = enc_dec_data_test[1]
    decoder_target_data_test = enc_dec_data_test[2]
    

    #Encoder
    encoder_inputs = Input(shape=(None,))
    en_x =  Embedding(num_encoder_tokens, embedding_size)(encoder_inputs)
    encoder = LSTM(embedding_size, return_state=True, go_backwards=True)
    encoder_outputs, state_h, state_c = encoder(en_x)
    # We discard 'encoder_outputs' and only keep the states
    encoder_states = [state_h, state_c]

    #Set up the decoder, using 'encoder_states' as initial state
    decoder_inputs = Input(shape=(None,))
    dex =  Embedding(num_decoder_tokens, embedding_size)
    final_dex = dex(decoder_inputs)
    decoder_lstm = LSTM(embedding_size, return_sequences=True, return_state=True)

    decoder_outputs, _, _ = decoder_lstm(final_dex,
                                        initial_state=encoder_states)

    decoder_dense = Dense(num_decoder_tokens, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc'])

    model.summary()

    encoder_model = Model(encoder_inputs, encoder_states)

    #return (model, encoder_model, encoder_input_data , decoder_input_data, decoder_target_data, decoder_inputs, dex)
    return (model, encoder_model, 
            encoder_input_data_train , 
            decoder_input_data_train, 
            decoder_target_data_train, 
            encoder_input_data_test ,            
            decoder_input_data_test, 
            decoder_target_data_test, 
            dex, decoder_lstm, decoder_dense)