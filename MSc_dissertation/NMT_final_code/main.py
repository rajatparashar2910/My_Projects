from preProcessing.inputData import readLines
from preProcessing.preProcessing import pre_process_final
from training.model import create_model
#from training.training import train_model
from training.training import train_model_with_generators
from predictions.predictions import decode_sequence
from bleuScores.bleuScores import evaluate_model
import codecs
import pickle
import h5py



numSent = 1000000
trainSize = 800000


#Read sentences from files
lines = readLines(numSent)


#Pre-process
pre_proc_list = pre_process_final(lines, numSent)

print('Saving clean data to pickle') 
pickle.dump( pre_proc_list, open( "clean_data.p", "wb" ) )
print('Clean data saved') 

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

print('Creating Model')
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
dex = modelList[8]
decoder_lstm = modelList[9]
decoder_dense = modelList[10]

print ('Model created')

print('Training started')
#training
#model = train_model(model, encoder_input_data, decoder_input_data, decoder_target_data, 1024, 60, 0.2)
#model = train_model(model, 
#                     encoder_input_data_train , 
#                     decoder_input_data_train, 
#                     decoder_target_data_train, 
#                     encoder_input_data_test ,            
#                     decoder_input_data_test, 
#                     decoder_target_data_test,
#                     1024, 70)
                    
                    
model_after_training = train_model_with_generators(train, test, 
                                  model, 
                                  encoder_input_data_train , 
                                  decoder_input_data_train, 
                                  decoder_target_data_train, 
                                  encoder_input_data_test ,            
                                  decoder_input_data_test, 
                                  decoder_target_data_test,
                                  32, #batchSize
                                  10,  #numEpochs (loop)
                                  25000, #steps_per_epoch
                                  1)  #Inner epoch  
                                  
                                    
print('Training complete')                                                

model = model_after_training[0]
histLoss_train = model_after_training[1] 
histAcc_train = model_after_training[2]
histLoss_test = model_after_training[3]
histAcc_test = model_after_training[4]  

print('Saving model')
model.save('results/model_1M.h5')

print('Saving Model weights')
model.save_weights('results/model_weights_1M.h5')

print('Saving history files to pickle') 

pickle.dump( histLoss_train, open( "histLoss_train_full.p", "wb" ) )
pickle.dump( histAcc_train, open( "histAcc_train_full.p", "wb" ) )
pickle.dump( histLoss_test, open( "histLoss_test_full.p", "wb" ) )
pickle.dump( histAcc_test, open( "histAcc_test_full.p", "wb" ) )

print('All pickle files saved')
              

#BLEU Scores
print('Calculating BLEU Scores')

print('Training BLEU Scores:')
evaluate_model(encoder_input_data_train, 
                train, 
                0, 
                trainSize,
                embedding_size,
                input_token_index, 
                target_token_index, 
                dex, 
                decoder_lstm, 
                decoder_dense, 
                encoder_model)
                
print('Test BLEU Scores:')
evaluate_model(encoder_input_data_test, 
                test, 
                trainSize, 
                numSent,
                embedding_size,
                input_token_index, 
                target_token_index, 
                dex, 
                decoder_lstm, 
                decoder_dense, 
                encoder_model,
                trainSize)


print('***************Making Sample Predictions for TRAIN*************\n')

#Training predictions
input_sent_list_train = list()
source_sent_list_train = list()
target_sent_list_train = list()
print('Starting Training predictions')

for seq_index in [14077,20122,40035,40064, 40056, 40068, 40090, 40095, 40100, 40119, 40131, 40136, 40150, 50100, 
                   54000, 55000, 64236, 72356, 77777, 80000, 84511, 92345, 99999, 100001, 123456, 134567, 145667,
                   150000, 180000, 200000, 250000, 300000, 350000, 360000, 390000, 500000, 600000, 650000, 750000, 
                   900000, 950000, 990000]:

#for seq_index in [5, 10, 15, 20, 25, 50, 60, 70, 100, 200, 400, 500, 600, 700, 750, 790]:
    input_sent_train = encoder_input_data_train[seq_index: seq_index + 1]
    input_sent_list_train.append(input_sent_train)
    target_sent_list_train.append(train.eng[seq_index])
    source_sent_list_train.append(train.hindi[seq_index: seq_index + 1])
decoded_sentence_list_train = decode_sequence(input_sent_list_train, 
                                              embedding_size, 
                                              input_token_index, 
                                              target_token_index, 
                                              dex, 
                                              decoder_lstm, 
                                              decoder_dense, 
                                              encoder_model)


#print('*********Source************\n', source_sent_list_train)
print('*********Target************\n', target_sent_list_train)
print('*********Decoded sentence***********\n', decoded_sentence_list_train)



print('***************Making Sample Predictions for TEST*************\n')

offset = trainSize

#testing predictions
input_sent_list_test = list()
source_sent_list_test = list()
target_sent_list_test = list()
print('Starting testing predictions')


for seq_index in [1101000, 1102000, 1103000, 1104000, 1105000, 1106000, 1107000, 1108000]:
    input_sent_test = encoder_input_data_test[seq_index-offset : (seq_index-offset) + 1]
    input_sent_list_test.append(input_sent_test)
    target_sent_list_test.append(test.eng[seq_index])
    source_sent_list_test.append(test.hindi[seq_index: seq_index + 1])
decoded_sentence_list_test = decode_sequence(input_sent_list_test, 
                                              embedding_size, 
                                              input_token_index, 
                                              target_token_index, 
                                              dex, 
                                              decoder_lstm, 
                                              decoder_dense, 
                                              encoder_model)

#print('*********Source************\n', source_sent_list_test)
print('*********Target************\n', target_sent_list_test)
print('*********Decoded sentence***********\n', decoded_sentence_list_test)