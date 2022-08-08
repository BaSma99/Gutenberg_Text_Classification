# -*- coding: utf-8 -*-
"""Text_Classification_Group_Assignment(1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14OnT3pywvygx7VXt7DMeP0XRta2b-DBz

**Step1: Preparing our books and data**

1- Import important libraries
"""

# Commented out IPython magic to ensure Python compatibility.
#Install mlxtend which is a library of Python tools and extensions for data science.
# %pip install mlxtend --upgrade

#import nltk---->leading platform for building Python programs to work with human language data.
import nltk
nltk.download('punkt')    #downloading punctuations from NLTK
nltk.download("stopwords")  #download stopwords from NLTK
nltk.download("wordnet")  #downloading lemmatizers from NLTK
from nltk.corpus import gutenberg #a small selection of texts from the Project Gutenberg electronic text archive
from nltk.corpus import stopwords #importing stopwords
from nltk.stem import WordNetLemmatizer # algorithmic process of finding the lemma of a word depending on its meaning and context.

import math #This module provides access to the mathematical functions defined by the C standard.
import pandas as pd  #open source data analysis library 
import numpy as np   #a Python library used for working with arrays.
import re #a Python library used for working with regular expressions

import matplotlib.pyplot as plt #to make some plots to discover our data and results
import tensorflow as tf

from sklearn import preprocessing
from sklearn.utils import shuffle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
from mlxtend.evaluate import bias_variance_decomp

#Urllib package is the URL handling module for python. It is used to fetch URLs (Uniform Resource Locators). 
#It uses the urlopen function and is able to fetch URLs using a variety of different protocols.
from urllib import request

"""collect differnt 5 books from one category and for differnt 5 authors"""

#combine all URLs of our historical books on a list 
BooksURLs = ["https://www.gutenberg.org/files/24654/24654-8.txt" ,
             "https://www.gutenberg.org/files/22153/22153-0.txt" ,
             "https://www.gutenberg.org/files/23691/23691-8.txt" ,
             "https://www.gutenberg.org/files/14400/14400-8.txt" ,
             "https://www.gutenberg.org/files/18931/18931-8.txt"]

#make a list of book names and make a label for every book
BooksNames = ["Chaldea",
              "Pagan and Christian Rome",
              "Archeological Expedition to Arizona in 1895",
              "Egyptian Archaeology",
              "Archeological Investigations"]
BooksLabels = ["a", "b" ,"c", "d" , "e"]

#make a list of book authors
BooksAuthors = ["Zénaïde A. Ragozin",
                "Rodolfo Lanciani",
                "Jesse Walter Fewkes",
                "Gaston Camille Charles Maspero",
                "Gerard Fowke"]

Books=[]

"""**Step2: preprocessing the data and data cleaning**"""

from urllib import request
#for loop to get every book in BooksURLs list
for URL  in BooksURLs :
  response = request.urlopen(URL)
  raw = response.read().decode('utf8' , errors = 'replace')
  wordsList= re.findall(r"[a-zA-Z]{3,}", raw)
  #perform lemmetization on the data
  lemmatizer = WordNetLemmatizer()
  lemmitizedWords =[]
  for i in wordsList:
    words = i.lower()
    word = lemmatizer.lemmatize(words)
    #check if the word not in stopwords set
    if word not in set(stopwords.words('english')):
      lemmitizedWords.append(str(word))
  Books.append(lemmitizedWords)

#to ensure that every book have 200 partition, and every partition have 100 words.
BooksWords = []  #to combine all words together
#for loop to get the book             
for i in Books:
  l = i[0:(math.floor(len(i)/100)) * 100]
  BooksWords.append(l)
#to combine all lists of the words on a single dataframe
result = pd.DataFrame()
for i in range(len(BooksWords)):
    df = {}
    list_of_partitions =  [BooksWords[i][x:x+100] for x in range(0, len(BooksWords[i]), 100)]
    #to combine Book Authors in one column
    df['Author_of_Book']= BooksAuthors[i]
    #to combine Book Names in one column
    df['Title_of_Book']= BooksNames[i] 
    #to combine Book Labels in one column
    df['Label_of_Book'] = BooksLabels[i]
    #to combine Book Partitions in one column
    df['PartitionsList'] = list_of_partitions 
    data = pd.DataFrame(df)
    #for loop to join our data together
    for i in range(len(data)):
      data["PartitionsList"][i] = " ".join(data["PartitionsList"][i])
    final_result = data[:200]
    result = result.append(final_result)
#shuffle the result of combining all dataframes together
result = shuffle(result)

#print head of data
result.head(5)

#describe our result
result.describe()

#get some information about our result
result.info()

"""make a CountPlot to ensure that every book have 200 partition"""

import seaborn as sns
plt.figure(figsize=(10,10))
ax = sns.countplot(x=result["Label_of_Book"],  data=result, order = result["Label_of_Book"].value_counts().index )
for p, label in zip(ax.patches, result["Label_of_Book"].value_counts()):   
    ax.annotate(label, (p.get_x()+0.25, p.get_height()+0.5))

top= 10
for label in result['Title_of_Book'].unique():
    corpus = result[result["Title_of_Book"]==label]["PartitionsList"]
    lst_tokens = nltk.tokenize.word_tokenize(corpus.str.cat(sep=" "))
    fig, ax = plt.subplots(nrows=1, ncols=2,constrained_layout=True, figsize=(20, 4))
    fig.suptitle(f"THE MOST FREQUENT WORDS OF BOOK: {label} ", fontsize=15)

    #to draw the unigram gragh
    dic_words_freq = nltk.FreqDist(lst_tokens)
    result_unigram = pd.DataFrame(dic_words_freq.most_common(), 
                        columns=["Word","Freq"])
    result_unigram.set_index("Word").iloc[:10,:].sort_values(by="Freq").plot(
                    kind="barh", title="Unigram", ax=ax[0], 
                    legend=False).grid(axis='x')
    ax[0].set(ylabel=None)
    
    #to draw the bigram graph
    dic_words_freq = nltk.FreqDist(nltk.ngrams(lst_tokens, 2))
    result_bigram = pd.DataFrame(dic_words_freq.most_common(), 
                        columns=["Word","Freq"])
    result_bigram["Word"] = result_bigram["Word"].apply(lambda x: " ".join(
                    string for string in x) )
    result_bigram.set_index("Word").iloc[:10,:].sort_values(by="Freq").plot(
                    kind="barh", title="Bigrams", ax=ax[1],
                    legend=False).grid(axis='x')
    ax[1].set(ylabel=None)

"""make a wordcloud figure to get the most frequent 50 words in every book"""

import wordcloud #Python wordcloud library to create tag clouds
import string
#for loop to take every unique book in the column of Title_of_Book 
for n in result['Title_of_Book'].unique():
  books = result[result["Title_of_Book"]==n]["PartitionsList"]
 #to print the most frequent 50 words of the unique book
  print(f"\n THE MOST FREQUENT 50 WORDS OF BOOK CALLED: {n}\n")
  WordCloudGragh = wordcloud.WordCloud(background_color='black', max_words=50, max_font_size=40)
  WordCloudGragh = WordCloudGragh.generate(str(books))
  plt.axis('off')
  plt.imshow(WordCloudGragh, cmap=None)
  plt.show()

"""Now, we can split our data and preparing it for training"""

#split dataset into subsets that minimize the potential for bias in your evaluation and validation process.
from sklearn.model_selection import train_test_split

x= np.array(result['PartitionsList'])
y=np.array(result['Label_of_Book'])

res_X_train, res_X_test, res_y_train, res_y_test = train_test_split(x, y, test_size= 0.3, random_state= 42)

"""**Step3: Perform Feature Engineering**

1- Build the Model
"""

#from scikit learn library in python, we can draw the learning curve of the model
#to get more information------> https://scikit-learn.org/stable/auto_examples/model_selection/plot_learning_curve.html
#function to draw the learning curve of every model
def DrawLearningCurve(estimator, title, X, y, ylim=None, cv=None, n_jobs=1, train_sizes=np.linspace(.1, 1.0,5)): 
    #to draw the figure of the model
    plt.figure()
    #to write the title of the model
    plt.title(title)
    #ylim, Defines minimum and maximum y-values plotted
    if ylim is not None:
        plt.ylim(*ylim)
        #to define the labels names of the curve
    plt.xlabel("TRAINING DATASET")
    plt.ylabel("MODEL SCORE")

    train_sizes, train_scores, test_scores = learning_curve(estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    #to plot the learning curve
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    
    plt.plot(train_sizes, train_scores_mean, '-', color="r", label="Training score")
    
    plt.plot(train_sizes, test_scores_mean, '-', color="g", label="Cross-validation score")

    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='best');
    return plt

"""Importing important libraries for evaluate, accuracy, and confusion matrix for every model"""

from sklearn.model_selection import cross_val_score #to Evaluate a score by cross-validation.
from sklearn.model_selection import KFold #Provides train/test indices to split data in train/test sets. Split dataset into k consecutive folds (without shuffling by default).
from sklearn.metrics import confusion_matrix #to Compute confusion matrix to evaluate the accuracy of a classification.
from sklearn.metrics import accuracy_score #to compute Accuracy classification score.
from sklearn.metrics import classification_report #to Build a text report showing the main classification metrics.
from sklearn.metrics import plot_confusion_matrix #to polt the confusion matrix for visualization
from mlxtend.evaluate import bias_variance_decomp # for various loss functions.

#function to build the model, train and test the model, and apply K-fold cross validation 
def ModelBuilding(model, ModelName, X_train, X_test, y_train, y_test, cv ):
#define a variable to deal with each classification model
  global TrainingModel
  #to train the classification model
  TrainingModel = model.fit(X_train, y_train) 
  #to make prediction of X_test value and print the Classification report of the model
  global Model_Y_Prediction
  Model_Y_Prediction = model.predict(X_test)

#now we can apply k-fold validation 
  #calculate accuracy 
  accuracy = cross_val_score(estimator = model , X= X_train , y = y_train ,cv = cv)
  accuracy_avg = accuracy.mean()# measure the accuracy of the model (bais)
  test_accuracy = accuracy_score(y_test, Model_Y_Prediction)
  # Evaluate the model performance using metrics.accuracy_score to measure the score
  #print cross validation accuracy of every model
  print("THE CROSS VALIDATION ACCURACY IS: ", accuracy, "\n")
  #print average cross validation accuracy of every model
  print("THE AVERAGE CROSS VALIDATION ACCURACY IS: " , accuracy_avg, "\n")
  #print testing accuracy of every model
  print("THE TESTING ACCURACY IS: "  ,test_accuracy,"\n")
  #print classification report of every model
  print(classification_report(y_test, Model_Y_Prediction))
  # print Confusion Matrix of every model
  print('\nTHE CONFUSION MATRIS IS:\n')
  print(confusion_matrix(y_test, Model_Y_Prediction), "\n")
  plot_confusion_matrix(TrainingModel, X_test, y_test, xticks_rotation='vertical')
 #draw the learning curve of every model
  DrawLearningCurve(TrainingModel,"THE LEARNING CURVE OF: "+ ModelName,X_train, y_train, ylim=(0, 1.1), cv=cv, n_jobs=8)  
  print("\n")

"""Now we can calculate and predict where the prediction error"""

#function to predict the prediction error
def ErrorPrediction(X_train, y_train, X_test, y_test ,Model_Y_Prediction):
  TestLabels=np.array(y_test)
  ErrorsList  = [] 
  PredictionList = []
  RightLabel = []
  #for loop to predict the error while testing the model
  for i ,text in enumerate(res_X_test) :
    if Model_Y_Prediction[i] != TestLabels[i]:
      Errors = text
      ErrorsList.append(Errors)

      Truelabel = TestLabels[i]
      RightLabel.append(Truelabel)
      
      PredictedLabel = Model_Y_Prediction[i]
      PredictionList.append(PredictedLabel)
      #combine all in a new dataframe
  dataframmePrediction = pd.DataFrame()
  dataframmePrediction['Error'] = ErrorsList
  dataframmePrediction['Right Label']   = RightLabel
  dataframmePrediction['Predicted Label'] = PredictionList
#print which model did not classify well
  print("THE MODEL DID NOT CLASSIFY: " , len(ErrorsList), "\n")

  #make the label encoding
  label_encoder = preprocessing.LabelEncoder()

  X_train_copy = np.copy(X_train)
  X_test_copy = np.copy(X_test)
  y_train_copy = np.copy(y_train)
  y_test_copy = np.copy(y_test)
#calculate average bias and average variance of every classification model
  AverageExpectedLoss, AverageBias, AverageVariance = bias_variance_decomp(TrainingModel,
                                                              np.array(X_train_copy),
                                                              label_encoder.fit_transform(y_train_copy),
                                                              np.array(X_test_copy),
                                                              label_encoder.fit_transform(y_test_copy),
                                                              num_rounds=2, 
                                                              random_seed=123)
  #print average bias and average variance of every classification model
  print('THE AVERAGE BIAS IS: %.3f' % AverageBias, "\n")
  print('THE AVEARAGE VARIANCE IS: %.3f' % AverageVariance, "\n")
  print("\n")
  return dataframmePrediction

"""**Step3: perform Bag Of Words (BOW) transformation and apply it to different 3 classification models**:

1.   Support vector machine(SVM) classification Model
2.   Decision Tree Classification Model
3.   KNN classification Model

"""

from sklearn.feature_extraction.text import CountVectorizer #to Convert a collection of text documents to a matrix of token counts.

countVector= CountVectorizer()

"""A bag of words is a representation of text that describes the occurrence of words within a document. """

#perform BOW transformation on the partitionslist column
BOWVector = countVector.fit_transform(result['PartitionsList'])

BOW = pd.DataFrame(BOWVector.toarray(), columns=countVector.get_feature_names())

#print Bag Of Words
BOW

"""After performing Bow we can split result into train and test"""

BOW_X = BOWVector.toarray()
BOW_Y = result["Label_of_Book"]

#spliting the data
X_train, X_test, y_train, y_test = train_test_split(BOW_X, BOW_Y, test_size= 0.3, random_state= 42)

"""1- perform BOW transformation on SVM algorithm"""

#define the type of support vector machine algorithm
BagOfWords_SVM = svm.SVC(kernel='linear')

ModelBuilding(BagOfWords_SVM,"Support Vector Machine with Bag Of Words", X_train, X_test, y_train, y_test ,10)

BagOfWords_SVM_Error = ErrorPrediction(X_train, y_train, X_test, y_test ,Model_Y_Prediction)

display(BagOfWords_SVM_Error.head())

"""**Apply Decision-Tree algorithm on BOW Transformation**"""

# Train Decision Tree Classifer
from sklearn.datasets import load_iris #is a classic and very easy multi-class classification dataset.
from sklearn import tree #non-parametric supervised learning method used for classification and regression.

BagOfWords_DT = DecisionTreeClassifier(random_state=0, max_depth= 10, criterion= 'entropy', min_samples_leaf= 1)

ModelBuilding(BagOfWords_DT,"Bag Of Words with Decision Tree ", X_train, X_test, y_train, y_test ,10)

BagOfWords_DT_Error = ErrorPrediction(X_train, y_train, X_test, y_test ,Model_Y_Prediction)

display(BagOfWords_DT_Error.head())

"""**Apply KNN algorithm with BOW Transformation**"""

#Classifier implementing the k-nearest neighbors vote.
from sklearn.neighbors import KNeighborsClassifier

BagOfWords_KNN = KNeighborsClassifier(n_neighbors = 3, algorithm= 'kd_tree', p= 1)

ModelBuilding(BagOfWords_KNN,"KNN with BOW Transformation", X_train, X_test, y_train, y_test ,10)

BafOfWords_KNN_Error = ErrorPrediction(X_train, y_train, X_test, y_test ,Model_Y_Prediction)

display(BafOfWords_KNN_Error.head())

"""**Step4:  perform TF-IDF transformation and apply it to different 3 classification models**

1.   Support vector machine(SVM) classification Model
2.   Decision Tree Classification Model
3.   KNN classification Model


"""

#to Convert a collection of raw documents to a matrix of TF-IDF features.
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()

"""Term frequency (TF) vectors show how important words are to documents. They are computed by using: ![image.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAkcAAAAwCAMAAAAsJS6VAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAIoUExURf////7+/v39/erq6tbW1tPT0+Xl5fr6+vj4+ODg4Nzc3PPz8/X19c/Pz9TU1Onp6fn5+d/f38zMzNHR0ebm5vv7++Pj49DQ0LOzs5mZmbu7u/T09PHx8c3NzaSkpKmpqdra2vDw8PLy8uzs7OTk5Pf395iYmO3t7efn556enpGRkb+/v9fX16WlpZKSkry8vO7u7rW1tXp6epycnIqKim5ubo2NjcXFxeLi4r29vcjIyMTExMHBwYaGhnR0dLa2tvz8/J2dncvLy7Kystvb26CgoGxsbKqqqnFxcfb29rm5ubGxsbi4uHx8fKGhoWhoaH19fdXV1YGBgZubm5+fn5OTk6KiooKCguHh4bCwsKenp+/v75WVlYSEhNLS0m9vb4WFhaysrJqammpqarq6uuvr6+jo6LS0tJeXl3t7e3BwcI+Pj8nJyX9/f3d3d9jY2H5+fqOjo3l5ednZ2aioqK6ursLCwr6+vomJiXh4eI6OjsPDw6+vr11dXcbGxlFRUcfHx6urq01NTXV1dWJiYre3t62trc7OzsrKysDAwN3d3VpaWl9fX4CAgJaWlllZWWBgYIiIiG1tbZSUlIyMjHNzc4eHh4uLi15eXqampmZmZlZWVt7e3kpKSnJyckdHR4ODg5CQkGtra3Z2dlRUVGlpaWVlZVxcXFtbW2FhYWNjY2RkZFdXV0tLS1VVVWdnZ05OTkZGRlhYWElJSVNTU09PT0VFRQAAAHaERM8AAAC4dFJOU////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wD2iudBAAAACXBIWXMAABcRAAAXEQHKJvM/AAAQyElEQVR4Xu2cS2KkuBJFaw3MYBXsgt2wEGZMWQRDr++dc0Ok02mXnbbT3dWviEqDkETodxUf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)"""

#to Transform result to document-term matrix.
TFIDF = vectorizer.fit_transform(result['PartitionsList'])

#transform it to array
TFIDF_Vector = pd.DataFrame(TFIDF.toarray(), columns=vectorizer.get_feature_names())

#print the TF-IDF vector
TFIDF_Vector

"""Now, we can split our result to train and test after performing TF-IDF transformation"""

TFIDF_X= TFIDF.toarray()
TFIDF_Y = result['Label_of_Book']

#Split the data into train and test
TFIDF_X_train, TFIDF_X_test, TFIDF_Y_train, TFIDF_Y_test = train_test_split(TFIDF_X, TFIDF_Y, test_size= 0.3, random_state= 42)

TFIDF_X_train.shape

TFIDF_X_test.shape

TFIDF_Y_train.shape

TFIDF_Y_test.shape

"""Apply support vector machine (SVM) classifier on TF-IDF Transformation"""

TFIDF_SVM = svm.SVC(kernel='sigmoid')

ModelBuilding(TFIDF_SVM, "SVM with TFIDF", TFIDF_X_train, TFIDF_X_test, TFIDF_Y_train, TFIDF_Y_test ,10)

TFIDF_SVM_Error  = ErrorPrediction(TFIDF_X_train, TFIDF_Y_train, TFIDF_X_test, TFIDF_Y_test ,Model_Y_Prediction)

display(TFIDF_SVM_Error.head())

"""Apply Decision Tree on TF-IDF Tranformation


"""

TFIDF_DT = DecisionTreeClassifier(random_state=0, max_depth= 10)

ModelBuilding(TFIDF_DT, "Decision Tree classifier with TFIDF Transformation",  TFIDF_X_train, TFIDF_X_test, TFIDF_Y_train, TFIDF_Y_test ,10)

TFIDF_DT_Error = ErrorPrediction(TFIDF_X_train, TFIDF_Y_train, TFIDF_X_test, TFIDF_Y_test, Model_Y_Prediction)

display(TFIDF_DT_Error.head())

"""Apply KNN Classification model on TF-IDF Tranformation"""

TFIDF_KNN =  KNeighborsClassifier(n_neighbors = 5, algorithm= 'kd_tree', p=2)

ModelBuilding(TFIDF_KNN, "KNN classification model with TFIDF Transformation", TFIDF_X_train, TFIDF_X_test, TFIDF_Y_train, TFIDF_Y_test ,10)

TFIDF_KNN_Error = ErrorPrediction(TFIDF_X_train, TFIDF_Y_train, TFIDF_X_test, TFIDF_Y_test, Model_Y_Prediction)

display(TFIDF_KNN_Error.head())

"""**Step5:  perform N-gram transformation and apply it to different 3 classification models**

1.   Support vector machine(SVM) classification Model
2.   Decision Tree Classification Model
3.   KNN classification Model

N-grams are continuous sequences of words or symbols or tokens in a document. In technical terms, they can be defined as the neighbouring sequences of items in a document
"""

N_Gram_Vectorizer = CountVectorizer(ngram_range=(2,2))

N_Gram= N_Gram_Vectorizer.fit_transform(result['PartitionsList'])

N_Gram_Vector = pd.DataFrame(N_Gram.toarray(), columns = N_Gram_Vectorizer.get_feature_names() )

N_Gram_Vector

"""Now, we can split our result to train and test after performing N-Gram transformation

"""

N_Gram_X= TFIDF.toarray()
N_Gram_Y = result['Label_of_Book']

#Split the data into train and test
N_Gram_X_train, N_Gram_X_test, N_Gram_Y_train, N_Gram_Y_test = train_test_split(N_Gram_X, N_Gram_Y, test_size= 0.3, random_state= 42)

N_Gram_X_train.shape

"""Apply support vector machine (SVM) classifier on N_Gram Transformation"""

N_Gram_SVM = svm.SVC(kernel='linear')

ModelBuilding(N_Gram_SVM, "SVM Classification Model with N-Gram Transformation", N_Gram_X_train, N_Gram_X_test, N_Gram_Y_train, N_Gram_Y_test ,10)

N_Gram_SVM_Error  = ErrorPrediction(N_Gram_X_train, N_Gram_Y_train, N_Gram_X_test, N_Gram_Y_test ,Model_Y_Prediction)

display(N_Gram_SVM_Error.head())

"""Apply Decision Tree on `N_Gram` Tranformation

"""

N_Gram_DT = DecisionTreeClassifier(random_state=0, max_depth= 10)

ModelBuilding(N_Gram_DT, "Decision Tree classifier with N_Gram Transformation",  N_Gram_X_train, N_Gram_X_test, N_Gram_Y_train, N_Gram_Y_test ,10)

N_Gram_DT_Error = ErrorPrediction(N_Gram_X_train, N_Gram_Y_train, N_Gram_X_test, N_Gram_Y_test, Model_Y_Prediction)

display(N_Gram_DT_Error)

"""Apply KNN classification model on `N_Gram` Tranformation

"""

N_Gram_KNN =  KNeighborsClassifier(n_neighbors = 5, algorithm= 'kd_tree', p=2)

ModelBuilding(N_Gram_KNN, "KNN classification model with N_Gram Transformation", N_Gram_X_train, N_Gram_X_test, N_Gram_Y_train, N_Gram_Y_test ,10)

N_Gram_KNN_Error = ErrorPrediction(N_Gram_X_train, N_Gram_Y_train, N_Gram_X_test, N_Gram_Y_test, Model_Y_Prediction)

display(N_Gram_KNN_Error)

"""**Step6: choose the champion model**

**After implementing the 3 algorithms, we can say that----> the champion model is SVM classification Model with TF-IDF transformation**, 
**IT has the highest accuracy and the lowest Bias and Variance**
"""

#Change the kernel type and degree make the accuracy go down
SVM_TFIDF_Low = svm.SVC(kernel = 'poly', max_iter= 3)

ModelBuilding(SVM_TFIDF_Low, "SVM classification model with TF-IDF Transformation", TFIDF_X_train, TFIDF_X_test, TFIDF_Y_train, TFIDF_Y_test ,10)

SVM_TFIDF_Low_Error  = ErrorPrediction(TFIDF_X_train, TFIDF_Y_train, TFIDF_X_test, TFIDF_Y_test ,Model_Y_Prediction)

display(SVM_TFIDF_Low_Error)

"""**Step7: Perform Error Analysis**

perform Error Analysis on the champion model (SVM with TF-IDF)
"""

TFIDF_SVM_Error

"""The svm model can't predict 8 columns, the error is in classes"d,c,e"."""

#print the most frequent words of error in index 0
wc = wordcloud.WordCloud(background_color='black', max_words=50, max_font_size=35)
wc = wc.generate(TFIDF_SVM_Error['Error'][0])
plt.axis('off')
plt.imshow(wc, cmap=None)
plt.show()

#print error words for index 0 of misclassified TF-IDF transformation and SVM model
TFIDF_SVM_Error['Error'][0]

#print the most frequent words of error in index 1
wc = wordcloud.WordCloud(background_color='black', max_words=50, max_font_size=35)
wc = wc.generate(TFIDF_SVM_Error['Error'][1])
plt.axis('off')
plt.imshow(wc, cmap=None)
plt.show()

#print error words for index 1 of misclassified TF-IDF transformation and SVM model
TFIDF_SVM_Error['Error'][1]

#print the most frequent words of error in index 2
wc = wordcloud.WordCloud(background_color='black', max_words=50, max_font_size=35)
wc = wc.generate(TFIDF_SVM_Error['Error'][2])
plt.axis('off')
plt.imshow(wc, cmap=None)
plt.show()

#print error words for index 2 of misclassified TF-IDF transformation and SVM model
TFIDF_SVM_Error['Error'][2]

#print the most frequent words of error in index 3
wc = wordcloud.WordCloud(background_color='black', max_words=50, max_font_size=35)
wc = wc.generate(TFIDF_SVM_Error['Error'][3])
plt.axis('off')
plt.imshow(wc, cmap=None)
plt.show()

#print error words for index 3 of misclassified TF-IDF transformation and SVM model
TFIDF_SVM_Error['Error'][3]

"""#Trying to do Data augmentation with reinforcement learning"""

#install numpy requests for data augmentation
!pip install numpy requests nlpaug

#to install data augmentation from github
!pip install numpy git+https://github.com/makcedward/nlpaug.git

!pip install torch>=1.6.0 transformers>=4.0.0 sentencepiece
# For Antonym and Synonym augmentations
!pip install nltk

#import important libraries for text data augmentation
import nlpaug.augmenter.sentence as nas
import nlpaug.flow as nafc
from nlpaug.util import Action
from tqdm import tqdm

from nlpaug.util.file.download import DownloadUtil

# download word2vec
DownloadUtil.download_word2vec(dest_dir='.')
DownloadUtil.download_glove(model_name='glove.6B', dest_dir='.') 

# download fasttext model
DownloadUtil.download_fasttext(model_name='wiki-news-300d-1M', dest_dir='.')

sentences = result['PartitionsList']

import nlpaug.augmenter.word as naw

aug = naw.ContextualWordEmbsAug(
        model_path='bert-base-uncased', action="insert")
for i, text in enumerate(sentences):
    augmented_text = aug.augment(text)
    print(f"{i + 1}:", augmented_text)

"""That's all what we tried to do from the paper"""