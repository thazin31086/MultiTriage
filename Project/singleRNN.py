#Single Task RNN Model
def RNNModel(btype_labels_map,dev_labels_map,btype_y_train,dev_y_train,btype_y_test,dev_y_test,splitno,DEV_PREDICT):
  from datetime import datetime
  #Logging 
  LR = str(Learningrate).replace('.','')

  if DEV_PREDICT == True: 
    predictwhat = 'DEVPREDICT'
  else:
    predictwhat = 'BUGPREDICT'

  if DataAugmentation == True:
   filename = DataFilePath + 'Results/RNNModel' + '_' + DataFileName + '_' + predictwhat + '_' + 'DataAug' + '_' + LR + '_' + str(EMBEDDING_DIM) + '_' + str(MAX_SEQUENCE_LENGTH) + '_S' +  str(splitno)
  else:
   filename = DataFilePath + 'Results/RNNModel' + '_' + DataFileName + '_' + predictwhat + '_' + LR + '_' + str(EMBEDDING_DIM) + '_' + str(MAX_SEQUENCE_LENGTH) + '_S' + str(splitno)

  filelog = open(filename + ".txt", "w")
  filelog.write("StartTime:" + str(datetime.now()))
  filelog.close()
  
  VALIDATION_SPLIT = 0.2
  noofbugtype = len(btype_labels_map)
  noofdev = len(dev_labels_map)
  btype_y_train = np.array(btype_y_train)
  dev_y_train = np.array(dev_y_train)
  btype_y_test = np.array(btype_y_test)
  dev_y_test = np.array(dev_y_test)

  #Visualize Model
  logdir = "logs/"
  tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
  #A model.fit() training loop will check at end of every epoch whether the loss is no longer decreasing, considering the min_delta and patiencez
  earlystop = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)

  if DEV_PREDICT == True:
    print('Predict Developer')
      # inputs
    input_context = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype=tf.float32, name="Bug_TitleandDescription") #Bug Title and Description 
    input_AST = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype=tf.float32, name ="Bug_CodeSnippetAST") #Bug Code Snippet AST
    emb_Context = Embedding(input_dim=len(tk_context.word_index) + 2, input_length=MAX_SEQUENCE_LENGTH, output_dim= EMBEDDING_DIM)(input_context)
    emb_AST = Embedding(input_dim=len(tk_AST.word_index) + 2, input_length=MAX_SEQUENCE_LENGTH, output_dim= EMBEDDING_DIM)(input_AST)
    cat = concatenate([emb_Context, emb_AST])
    sd = SpatialDropout1D(0.5)(cat)
    #Bidirectional layer will enable our model to predict a missing word in a sequence, 
    #So, using this feature will enable the model to look at the context on both the left and the right.
    bilstm = Bidirectional(LSTM(25, return_sequences=True))(sd)
    bn = BatchNormalization()(bilstm)
    drop = Dropout(0.5)(bn) 
    maxpool = GlobalMaxPool1D()(drop)
    dense = Dense(50,activation = 'relu')(maxpool)
    final = Dense(noofdev, activation = 'sigmoid') (dense)
    Bil_LSTM_model = Model(inputs=[input_context, input_AST], outputs=[final])
    
    Bil_LSTM_model.compile(loss='binary_crossentropy', optimizer=Adam(Learningrate), metrics=['accuracy',c_precision,c_recall,'AUC', c_fbeta,c_f1_macro,hammingloss])

    csv_logger = CSVLogger(filename + '.csv', append=True, separator=',')
    history = Bil_LSTM_model.fit([x_train_context, x_train_AST], 
                dev_y_train, 
                callbacks=[tensorboard_callback,earlystop,csv_logger],
                epochs=50, verbose=2, validation_split= 0.1)
      
    ## Evaluate RNN Single Model 
    
    evaluate = Bil_LSTM_model.evaluate([x_test_context, x_test_AST], dev_y_test)
    df_evaluate = pd.DataFrame(columns=['loss','accuracy','c_precision','c_recall', 'auc', 'c_fbeta', 'c_f1_macro', 'hammingloss'])
    df_row = {'loss': evaluate[0], 'accuracy': evaluate[1],'c_precision': evaluate[2],
              'c_recall': evaluate[3], 'auc': evaluate[4], 'c_fbeta': evaluate[5],
              'c_f1_macro': evaluate[6], 'hammingloss': evaluate[7]}
    df_evaluate= df_evaluate.append(df_row, ignore_index=True)
    df_evaluate.to_csv(filename + "_eval.csv")   

    filelog =  open(filename + ".txt","a")
    filelog.write("Endtime:" + str(datetime.now()))
    filelog.close() 

  else: 
    print('Predict Bug Type')
      # inputs
    input_context = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype=tf.float32, name="Bug_TitleandDescription") #Bug Title and Description 
    input_AST = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype=tf.float32, name ="Bug_CodeSnippetAST") #Bug Code Snippet AST
    emb_Context = Embedding(input_dim=len(tk_context.word_index) + 2, input_length=MAX_SEQUENCE_LENGTH, output_dim= EMBEDDING_DIM)(input_context)
    emb_AST = Embedding(input_dim=len(tk_AST.word_index) + 2, input_length=MAX_SEQUENCE_LENGTH, output_dim= EMBEDDING_DIM)(input_AST)
    cat = concatenate([emb_Context, emb_AST])
    sd = SpatialDropout1D(0.5)(cat)
    #Bidirectional layer will enable our model to predict a missing word in a sequence, 
    #So, using this feature will enable the model to look at the context on both the left and the right.
    bilstm = Bidirectional(LSTM(25, return_sequences=True))(sd)
    bn = BatchNormalization()(bilstm)
    drop = Dropout(0.5)(bn)
    maxpool = GlobalMaxPool1D()(drop)
    dense = Dense(50,activation = 'relu')(maxpool)
    final = Dense(noofbugtype, activation = 'sigmoid') (dense)
    Bil_LSTM_model = Model(inputs=[input_context, input_AST], outputs=[final])
    
    Bil_LSTM_model.compile(loss='binary_crossentropy', optimizer=Adam(Learningrate), metrics=['accuracy',c_precision,c_recall,'AUC', c_fbeta,c_f1_macro,hammingloss])
    
    csv_logger_bug = CSVLogger(filename + '.csv', append=True, separator=',')
    history = Bil_LSTM_model.fit([x_train_context, x_train_AST], 
                btype_y_train, 
                callbacks=[tensorboard_callback,earlystop,csv_logger_bug],
                epochs=50, verbose=2, validation_split= 0.1)
      
    ## Evaluate RNN Single Model 
    evaluate= Bil_LSTM_model.evaluate([x_test_context, x_test_AST], btype_y_test)
    df_evaluate = pd.DataFrame(columns=['loss','accuracy','c_precision','c_recall', 'auc', 'c_fbeta', 'c_f1_macro', 'hammingloss'])
    df_row = {'loss': evaluate[0], 'accuracy': evaluate[1],'c_precision': evaluate[2],
              'c_recall': evaluate[3], 'auc': evaluate[4], 'c_fbeta': evaluate[5],
              'c_f1_macro': evaluate[6], 'hammingloss': evaluate[7]}
    df_evaluate= df_evaluate.append(df_row, ignore_index=True)
    df_evaluate.to_csv(filename + "_eval.csv") 

    filelog =  open(filename + ".txt","a")
    filelog.write("Endtime:" + str(datetime.now()))
    filelog.close() 
