#Multi-Triage Model
def MultiModel(project,btype_labels_map,dev_labels_map,btype_y_train,dev_y_train,btype_y_test,dev_y_test,dataaug,MAX_SEQUENCE_LENGTH,EMBEDDING_DIM): 
  #Logging 
  filename = 'Multimodel' + '_' + project + '_' + dataaug + '_' + Learningrate + '_' + EMBEDDING_DIM + '_' + MAX_SEQUENCE_LENGTH 
  filelog = open(filename + ".txt", "w")
  filelog.write("StartTime:" + str(datetime.now()))
  filelog.close()

  #Paramaters
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

  starttime = datetime.now()
  print("Start Time =", starttime)
  print('Predict Developer')
  
  # inputs
  input_context = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype=tf.float32, name="Bug_TitleandDescription") #Bug Title and Description 
  input_AST = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype=tf.float32, name ="Bug_CodeSnippetAST") #Bug Code Snippet AST

  #Context Enconder
  emb_Context = Embedding(input_dim=len(tk_context.word_index) + 2, input_length=MAX_SEQUENCE_LENGTH, output_dim= EMBEDDING_DIM,name ="Context_Embedding")(input_context)
  conv_Context = Conv1D(filters=64, kernel_size=2, padding='same', activation='relu', name ="Context_Convolutional_Layer")(emb_Context)
  maxpool_Context = GlobalMaxPool1D(name ="Context_Maxpool_Layer")(conv_Context)
  flatcon = Flatten(name ="Context_Flatten_Layer")(maxpool_Context)

  
  #AST Enconder
  emb_AST = Embedding(input_dim=len(tk_AST.word_index) + 2, input_length=MAX_SEQUENCE_LENGTH, output_dim= EMBEDDING_DIM, name ="AST_Embedding")(input_AST)
  bilstm_AST = Bidirectional(LSTM(25, return_sequences=True, name ="AST_LSTM_Layer"))(emb_AST)
  maxpool_AST = GlobalMaxPool1D(name ="AST_Maxpool_Layer")(bilstm_AST)
  flatAST = Flatten(name ="AST_Flatten_Layer")(maxpool_AST)

  cat = concatenate([flatcon,flatAST], name="Concatenate_Flatten_Layer")
 
  bn = BatchNormalization()(cat)
  drop = Dropout(0.5)(bn)
  dense = Dense(50,activation = 'relu')(drop)
  DevOutput = Dense(noofdev, activation = 'sigmoid',name="Developer") (dense)
  BugTypeOutput = Dense(noofbugtype, activation = 'sigmoid', name="Bug_Type") (dense)
  Bil_LSTM_MultiTask_model = Model(inputs=[input_context, input_AST], outputs=[DevOutput,BugTypeOutput])
    
  Bil_LSTM_MultiTask_model.compile(loss='binary_crossentropy', optimizer=Adam(Learningrate), metrics=['accuracy',c_precision,c_recall,'AUC', c_f1_macro, c_fbeta, hammingloss])

  history = Bil_LSTM_MultiTask_model.fit([x_train_context, x_train_AST], 
                [dev_y_train, btype_y_train], 
                callbacks=[tensorboard_callback,earlystop],
                epochs=50, verbose=2, validation_split= 0.1)
      
  ## Evaluate RNN Single Model 
  csv_logger = CSVLogger(filename + '.csv', append=True, separator=';')
  Bil_LSTM_MultiTask_model.evaluate([x_test_context, x_test_AST], [dev_y_test, btype_y_test], callbacks=[csv_logger])
  
  filelog =  open(filename + ".txt","a")
  filelog.write("Endtime:" + str(datetime.now()))
  filelog.close() 
