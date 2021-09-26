# Remove stopwords
def Cleandata(data):
  porter = PorterStemmer()
  for ind in data.index: 
    bug_description = data['Title_Description'][ind]
    bug_description= re.sub("[^a-zA-Z]", " ", str(bug_description))
    if bug_description and bug_description.strip():
      tk_bug_description = word_tokenize(bug_description)
      tokens_without_sw = str([word for word in tk_bug_description if not word in stopwords.words('english')]).strip('[]').replace("'","").replace(",","").replace("\\","")
      tokens_without_sl = ' '.join([w for w in tokens_without_sw.split() if len(w)>1]) #token without single letter
      tokens_with_stemm = ' '.join([porter.stem(w) for w in tokens_without_sl.split()]) #token with stemm
      data['Title_Description'][ind] = tokens_with_stemm
  return data

def create_tag_mapping(mapping_csv, tagname):
  print('tagname', tagname)
  # create a set of all known tags
  labels = set()
  IssueType_Tags = []
  for i in range(len(mapping_csv)):
    # convert spaced separated tags into an array of tags
    tags = mapping_csv[i].split('|')
    # add tags to the set of known labels
    labels.update(tags)
    
  # convert set of labels to a list to list
  labels = list(labels)
  # order set alphabetically
  labels.sort()
  # dict that maps labels to integers, and the reverse
  labels_map = {labels[i]:i for i in range(len(labels))}
  inv_labels_map = {i:labels[i] for i in range(len(labels))}  

  for i in range(len(mapping_csv)): 
    # Create One Hot Encoding For Issue Type 
    IssueType_Tag = one_hot_encode(mapping_csv[i].split('|'), labels_map)
    IssueType_Tags.append(IssueType_Tag)
    
  result = IssueType_Tags
  return labels_map, inv_labels_map, result

#########SplitTrainTestData################
def SplitTrainTestData(data): 
  x_train_context = []
  x_train_AST = []
  dev_y_train = []
  btype_y_train = [] 
  x_test_context = []
  x_test_AST = []
  dev_y_test = []
  btype_y_test = []
  tk_context = []
  
  dev_y = list(data['FixedByID'].astype(str)) # Developer List
  btype_y = list(data['Name'].astype(str))  # Bug Type List
  data.Title_Description = data.Title_Description.astype(str)
  x_context = list(data['Title_Description'])
  data.AST = data.AST.astype(str)
  x_AST = list(data['AST'])

  #80% / 20% train / test split:
  train_size = int(len(x_context) * .8)

  x_train_context = x_context[:train_size]
  x_train_AST = x_AST[:train_size]
  dev_y_train = dev_y[:train_size]
  btype_y_train = btype_y[:train_size]

  x_test_context = x_context[train_size:]
  x_test_AST = x_AST[train_size:]
  dev_y_test = dev_y[train_size:]
  btype_y_test = btype_y[train_size:]
  
  #/*******************Label Encoder***********************/
  ### Developer Encoder 
  combineddata_dev = dev_y_train + dev_y_test
  dev_labels_map,dev_inv_labels_map,combineddata_dev_enc = create_tag_mapping(combineddata_dev,'FixedByID')
  dev_y_train = combineddata_dev_enc[:len(dev_y_train)]
  dev_y_test = combineddata_dev_enc[len(dev_y_train):]
  print("Developer","Training: ", len(dev_y_train), "Testing :",len(dev_y_test), "Combined DEV + TEST", len(combineddata_dev_enc))

    ### BugType Encoder
  combineddata_bugtype = btype_y_train + btype_y_test
  btype_labels_map,btype_inv_labels_map,combineddata_bugtype_enc = create_tag_mapping(combineddata_bugtype,'Name')
  btype_y_train = combineddata_bugtype_enc[:len(btype_y_train)]
  btype_y_test = combineddata_bugtype_enc[len(btype_y_train):]
  print("Bug Type","Training: ", len(btype_y_train), "Testing :",len(btype_y_test), "Combined DEV + TEST", len(combineddata_bugtype_enc))

  # Tokenizer
  x_train_context =[str(row).lower() for row in x_train_context]
  x_test_context =[str(row).lower() for row in x_test_context]
  combineddata = x_train_context + x_test_context
  tk_context = Tokenizer(num_words=None, char_level=None, oov_token='Unknown',filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n\d+')
  tk_context.fit_on_texts(combineddata)

  return tk_context, x_train_context,x_train_AST, dev_y_train, btype_y_train, x_test_context, x_test_AST, dev_y_test, btype_y_test, dev_labels_map, dev_inv_labels_map, btype_labels_map, btype_inv_labels_map

def SplitTrainTestDataForMultiLabelWithDataAugmentation(data,splitno):
    x_train_context = []
    x_train_AST = []
    dev_y_train = []
    btype_y_train = [] 
    x_test_context = []
    x_test_AST = []
    dev_y_test = []
    btype_y_test = []
    tk_context = []

    if LoadDataAugFromFile == True: 
      traindata = pd.read_csv(DataFilePath + 'DataAugmentation/'+ DataFileName + 'trainaugdata' + splitno + FileType, error_bad_lines=False, index_col=False, dtype='unicode', encoding='latin-1',low_memory=False).sample(frac=1)
      traindata = traindata.rename(columns = {'ï»¿RepoID': 'RepoID'}, inplace = False)

      testdata = pd.read_csv(DataFilePath + 'DataAugmentation/' + DataFileName + 'testdata' + splitno +  FileType, error_bad_lines=False, index_col=False, dtype='unicode', encoding='latin-1',low_memory=False).sample(frac=1)
      testdata = testdata.rename(columns = {'ï»¿RepoID': 'RepoID'}, inplace = False)
      testdata = RemoveTestRecordIfNotExistInTrainData(traindata, testdata)
    else:
      #80% / 20% train / test split:
      train_size = int(len(data) * .8)
      traindata = data[:train_size]
      testdata = data[train_size:]
      #Save Data to TestFile
      testfilename = DataFileName + 'testdata' + splitno + FileType
      testdata.to_csv(testfilename)
      #/*Create Sample Data*/
      traindata = CreateOversamplingWithDataAugmentation(traindata,splitno)
    
    #/*****************Train Data***********************/
    train_dev_y = list(traindata['FixedByID']) # Developer List
    train_btype_y = list(traindata['Name'])  # Bug Type List
    train_x_context = list(traindata['Title_Description'])
    traindata.AST = traindata.AST.astype(str)
    train_x_AST = list(traindata['AST'])

    x_train_context = train_x_context
    x_train_AST = train_x_AST

    #/****************Test Data************************/
    x_test_context = list(testdata['Title_Description'])
    x_test_AST = list(testdata['Title_Description'])
    test_dev_y = list(testdata['FixedByID']) # Developer List
    test_btype_y = list(testdata['Name'])  # Bug Type List

    #/*******************Label Encoder***********************/ 
    ### Developer Encoder 
    combineddata_dev = train_dev_y + test_dev_y
    dev_labels_map,dev_inv_labels_map,combineddata_dev_enc = create_tag_mapping(combineddata_dev,'FixedByID')
    dev_y_train = combineddata_dev_enc[:len(train_dev_y)]
    dev_y_test = combineddata_dev_enc[len(train_dev_y):]
    print("Developer","Training: ", len(train_dev_y), "Testing :",len(test_dev_y), "Combined DEV + TEST", len(combineddata_dev_enc))

    ### BugType Encoder
    combineddata_bugtype = train_btype_y + test_btype_y
    btype_labels_map,btype_inv_labels_map,combineddata_bugtype_enc = create_tag_mapping(combineddata_bugtype,'Name')
    btype_y_train = combineddata_bugtype_enc[:len(train_btype_y)]
    btype_y_test = combineddata_bugtype_enc[len(train_btype_y):]
    print("Bug Type","Training: ", len(btype_y_train), "Testing :",len(btype_y_test), "Combined DEV + TEST", len(combineddata_bugtype_enc))

    #/*******************Tokenizer****************************/

    x_train_context =[str(row).lower() for row in x_train_context]
    x_test_context =[str(row).lower() for row in x_test_context]
    combineddata = x_train_context + x_test_context
    tk_context = Tokenizer(num_words=None, char_level=None, oov_token='Unknown',filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n\d+')
    tk_context.fit_on_texts(combineddata)

    return traindata, tk_context, x_train_context,x_train_AST, dev_y_train, btype_y_train, x_test_context, x_test_AST, dev_y_test, btype_y_test, dev_labels_map, dev_inv_labels_map, btype_labels_map, btype_inv_labels_map

def Tokenize(tk_context, x_train_context,x_train_AST, x_test_context, x_test_AST):
    #=======================Convert string to index================
    # Tokenizer
    x_train_context =[str(row).lower() for row in x_train_context]
    x_test_context =[str(row).lower() for row in x_test_context]
    combineddata_context = x_train_context + x_test_context
    tk_context = Tokenizer(num_words=None, char_level=None, oov_token='Unknown',filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
    tk_context.fit_on_texts(combineddata_context)

    x_train_AST =[str(row).lower() for row in x_train_AST]
    x_test_AST =[str(row).lower() for row in x_test_AST]
    combineddata_AST = x_train_AST + x_test_AST
    tk_AST = Tokenizer(num_words=None, char_level=None, oov_token='Unknown')
    tk_AST.fit_on_texts(combineddata_AST)

    # Convert string to index 
    x_train_context_sequences = tk_context.texts_to_sequences(x_train_context)
    x_train_AST_sequences = tk_AST.texts_to_sequences(x_train_AST)
    x_test_context_sequences = tk_context.texts_to_sequences(x_test_context)
    x_test_AST_sequences = tk_AST.texts_to_sequences(x_test_AST)

    # Padding
    x_train_context = pad_sequences(x_train_context_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
    x_train_AST = pad_sequences(x_train_AST_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
    x_test_context = pad_sequences(x_test_context_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
    x_test_AST = pad_sequences(x_test_AST_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')

    # Convert to numpy array
    x_train_context = np.array(x_train_context)
    x_train_AST = np.array(x_train_AST)
    x_test_context = np.array(x_test_context)
    x_test_AST = np.array(x_test_AST)
    return tk_context, tk_AST, x_train_context,x_train_AST, x_test_context, x_test_AST 

## Remove record if does not exist in TrainData
def RemoveTestRecordIfNotExistInTrainData(traindata, testdata):
    traingroup = traindata.groupby(["Name","FixedByID"],as_index=True)["FixedByID"].size().reset_index(name="count")
    testgroup = testdata.groupby(["Name","FixedByID"],as_index=True)["FixedByID"].size().reset_index(name="count")
    for ind in testgroup.index:
      try:
        record = traindata[traindata['FixedByID'].str.match(testgroup['FixedByID'][ind]) & traindata['Name'].str.match(testgroup['Name'][ind])]
        if len(record) < 1:
            print('remove from testdata...')
            testdata= testdata.drop(testdata[testdata['FixedByID'].str.match(testgroup['FixedByID'][ind]) & testdata['Name'].str.match(testgroup['Name'][ind])].index)
      except:
        print("An exception occurred index :",ind)    
    return testdata

# create a one hot encoding for one list of tags
def one_hot_encode(tags, mapping):
    # create empty vector
    encoding = zeros(len(mapping), dtype='uint8')
    # mark 1 for each tag in the vector
    for tag in tags:
      encoding[mapping[tag]] = 1
    return encoding
