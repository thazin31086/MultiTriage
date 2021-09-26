## Oversample Record with Data Augmentation Group by Developer and Bug Type
def CreateOversamplingWithDataAugmentation(data,splitno):
    #/*Get Contextual Word Embedding Model*/
    aug = naw.ContextualWordEmbsAug(model_path='bert-base-uncased', action="substitute")
    #/*Get Developer Bug Count/
    dfcountbybug = data.groupby(["Name","FixedByID"],as_index=True)["FixedByID"].size().reset_index(name="count")
    dfcountbybug.to_csv('list.csv')
    #/*Get Minority Class List*/
    majoritycount = dfcountbybug[(dfcountbybug['FixedByID'] != 'unknown') & (dfcountbybug['Name'] != 'unknown')]['count'].max()  
    #/*Get Majority Class Count*/
    minoritylist = dfcountbybug[(dfcountbybug['count'] != dfcountbybug['count'].max())]
    print(majoritycount, len(minoritylist), majoritycount * len(minoritylist))
    estimatetotalnoofdataaugrecord =  majoritycount * len(minoritylist)
    maxnoofaug = majoritycount
    ## Data Aug Record Count Validation, If over threshold reduce the majaritycount
    if estimatetotalnoofdataaugrecord > DataAugThreshold: 
      print('Overtheshold--')
      maxnoofaug = int((DataAugThreshold/estimatetotalnoofdataaugrecord) * majoritycount)

    #/*Loop through Minor Class Group*/
    for ind in minoritylist.index: 
      #print(minoritylist['FixedByID'][ind], minoritylist['count'][ind]) 
      developer = minoritylist['FixedByID'][ind]
      bugtype = minoritylist['Name'][ind]
      minoritycount = minoritylist['count'][ind]
      data1 = data[(data['FixedByID'] == developer) & (data['Name'] == bugtype)]
      #print(len(data1), developer,bugtype)
      #print('minoritycount  --->',minoritycount, 'majoritycount--->',majoritycount, 'index --->', ind , 'out of ', len(minoritylist.index))
      #Create Sample Data until minority class count Match up with majority class count 
      while minoritycount < maxnoofaug:
        #majoritycount:
        samplerow = data1.sample()     
        oldbugdescription = str(samplerow['Title_Description'].values).strip('[]').replace("'","")
        if oldbugdescription:         
          first100words_aug = str(aug.augment(' '.join(oldbugdescription.split()[:100])))
          remainingwords = ' '.join(oldbugdescription.split()[100:])
          newbugdescription = first100words_aug +  remainingwords
          new_row = {'RepoID' : str(samplerow['RepoID'].values).strip('[]').replace("'",""), 
                    #'PullRequestID' : str(samplerow['PullRequestID'].values).strip('[]').replace("'",""),
                    'IssueID': str(samplerow['IssueID'].values).strip('[]').replace("'",""),
                    'Title_Description': newbugdescription, #/*Data Augmentation : Title_Desciption*/
                    'AST': str(samplerow['AST'].values).strip('[]').replace("'",""),
                    'FixedByID' : str(samplerow['FixedByID'].values).strip('[]').replace("'",""),
                    'Name': str(samplerow['Name'].values).strip('[]').replace("'",""),
                    'CreatedDate': str(samplerow['CreatedDate'].values).strip('[]').replace("'","")}
          data = data.append(new_row, ignore_index=True)
          minoritycount = minoritycount + 1
        gc.collect()
    trainfilename = DataFileName + 'trainaugdata' + splitno + FileType
    data.to_csv(trainfilename)
    return data
