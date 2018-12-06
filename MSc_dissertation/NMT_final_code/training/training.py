import matplotlib.pyplot as plt
#%matplotlib inline
import keras
from keras.layers import Input, LSTM, Embedding, Dense
from keras.models import Model
from keras.utils import plot_model
import tensorflow as tf

def call_generators(dataframe, encoder_input_data, decoder_input_data, decoder_target_data, batchSize):
    while True:
        for i in range( 0 , len(dataframe)-batchSize , batchSize ):
            inds = range (i , i + batchSize )
            yield [ encoder_input_data[inds ] , decoder_input_data[ inds ] ] , decoder_target_data[ inds ] 


def train_model_with_generators(train, test, 
                                  model, 
                                  encoder_input_data_train , 
                                  decoder_input_data_train, 
                                  decoder_target_data_train, 
                                  encoder_input_data_test ,            
                                  decoder_input_data_test, 
                                  decoder_target_data_test,
                                  batchSize, 
                                  numEpochs,
                                  epochSteps,
                                  insideEpoch):
  tr_gen =  call_generators(train, encoder_input_data_train, decoder_input_data_train, decoder_target_data_train, batchSize)
  test_gen = call_generators(test, encoder_input_data_test, decoder_input_data_test, decoder_target_data_test, batchSize)
  
  histLoss_train = list()
  histAcc_train = list()
  histLoss_test = list()
  histAcc_test = list()
  
  for ep in range( numEpochs ):
      print ("Epoch" , ep)
      history = model.fit_generator( tr_gen ,
                              steps_per_epoch= epochSteps, 
                              epochs=insideEpoch , 
                              validation_data= test_gen, 
                              validation_steps=6250,
                              shuffle = True  )
  
      histLoss_train.append(history.history['loss'])
      histAcc_train.append(history.history['acc'])
      histLoss_test.append(history.history['val_loss'])
      histAcc_test.append(history.history['val_acc'])                            
  
  return model, histLoss_train, histAcc_train, histLoss_test, histAcc_test


def train_model(model, 
                encoder_input_data_train , 
                decoder_input_data_train, 
                decoder_target_data_train, 
                encoder_input_data_test ,            
                decoder_input_data_test, 
                decoder_target_data_test, 
                batchSize, numEpochs):

    #model.fit([encoder_input_data, decoder_input_data], decoder_target_data, batch_size = batchSize, epochs = numEpochs)
    
    model.fit([encoder_input_data_train, decoder_input_data_train], decoder_target_data_train,
               batch_size=batchSize,
               epochs=numEpochs,
               validation_data= ([encoder_input_data_test, decoder_input_data_test], decoder_target_data_test), shuffle = True)
    
    # # summarize history for accuracy
    # plt.plot(history.history['acc'])
    # plt.plot(history.history['val_acc'])
    # plt.title('Model Accuracy')
    # plt.ylabel('Accuracy')
    # plt.xlabel('Epoch')
    # plt.legend(['train', 'test'], loc='upper left')
    # plt.show()

    # # summarize history for loss
    # plt.plot(history.history['loss'])
    # plt.plot(history.history['val_loss'])
    # plt.title('model loss')
    # plt.ylabel('loss')
    # plt.xlabel('epoch')
    # plt.legend(['train', 'test'], loc='upper left')
    # plt.show()

    return model