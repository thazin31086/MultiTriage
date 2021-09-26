
# MultiTriage 

A neural network based bug triage learning model to recommend the list of developers and issue types most relevant to a new issue report.

# Requirements  
```sh
- python3 --version (>=3.7)
- TensorFlow - version (>=2.6)
```

# Quickstart

## Step 1 : Cloning this repository

```sh
git clone https://github.com/thazin31086/MultiTriage
cd MultiTriage
```

## Step 2: Creating a new dataset from C# OR Java sources
```sh
To use our model you can either used our preprocessed dataset from data folder, or download a new dataset of your own.
```

## Step 3: Preprocess a data
```
run main.py to preprocess the data 
Note: If you are using your own dataset, please use C# AST Extractor and Java# AST Extractor from https://github.com/tech-srl/code2vec to transform code snippet to AST path
```

## Step 4: Train model
```
run multirage.py to train multitriage model 
run singleCNN.py to train Single CNN model 
run singlRNN.py to train Single RNN model
```
