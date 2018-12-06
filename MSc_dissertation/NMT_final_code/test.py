model = train_model(model, encoder_input_data, decoder_input_data, decoder_target_data, 1024, 60, 0.2)
model = train_model(model, 
                    encoder_input_data_train , 
                    decoder_input_data_train, 
                    decoder_target_data_train, 
                    encoder_input_data_test ,            
                    decoder_input_data_test, 
                    decoder_target_data_test,
                    1024, 70)