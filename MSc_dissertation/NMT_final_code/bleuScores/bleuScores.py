from nltk.translate.bleu_score import corpus_bleu
from nltk.translate.bleu_score import SmoothingFunction
from predictions.predictions import decode_sequence


def evaluate_model(encoder_input_data, 
                    dataframe, 
                    startIndex, 
                    endIndex,
                    embedding_size,
                    input_token_index, 
                    target_token_index, 
                    dex, 
                    decoder_lstm, 
                    decoder_dense, 
                    encoder_model,
                    offset=0):
    source, actual, predicted = list(), list(), list()
    cc = SmoothingFunction()
    numLines = endIndex - startIndex
    print('Start Index is: ',startIndex)
    print('End Index is: ',endIndex)
    
    input_seq_list = encoder_input_data[startIndex-offset:endIndex-offset]
    print('Input seq list length: ', len(input_seq_list))
    #translation = decode_sequence(input_seq)
    translation = decode_sequence(input_seq_list,
                                   embedding_size,
                                   input_token_index, 
                                   target_token_index, 
                                   dex, 
                                   decoder_lstm, 
                                   decoder_dense, 
                                   encoder_model) 
    print ('Translation length: ',len(translation))
    predicted = predicted + translation        
    print('Predicted sentences length: ',len(predicted))  
    print('Predicted type: ', type(predicted))  
                                                            
    source = list(dataframe.hindi[startIndex-offset : endIndex-offset])
    print('Source sentences length: ',len(source)) 
    print('Source type: ', type(source))
    
    actual = list(dataframe.eng[startIndex-offset : endIndex-offset])
    print('Actual sentences length: ',len(actual)) 
    print('Actual type: ', type(actual))
    
    
    
#         if seq_index > 10000 and seq_index<10025:
#             print('input=[%s], target =[%s] predicted=[%s]' % (source, actual, predicted))
    print ('Translation completed!!!!!')  
      
    # calculate BLEU score
    print('BLEU-1: %f' % corpus_bleu(actual, predicted, weights=(1.0, 0, 0, 0)))
    #print('BLEU-2: %f' % corpus_bleu(actual, predicted, weights=(0.5, 0.5, 0, 0), smoothing_function=cc.method4))
    #print('BLEU-3: %f' % corpus_bleu(actual, predicted, weights=(0.33, 0.33, 0.33, 0), smoothing_function=cc.method4))
    print('BLEU-4: %f' % corpus_bleu(actual, predicted, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=cc.method4))
    
    print('BLEU score calculations done')