import sys, os
from numpy import *
from matplotlib.pyplot import *

from rnn_simple import RNNLM
from data_utils import utils as du
import pandas as pd


def read_training(filename):
  training_set = []
  with open(filename) as f:
    for i,line in enumerate(f):
      line=line.rstrip().split(',')
      current=[int(x) for x in line]
      training_set.append(current)
  return training_set

# Load the vocabulary

vocab = pd.read_table("worddic.txt",header=None,sep="\s+",index_col=0)

# Choose how many top words to keep
#vocabsize = 2000
vocabsize = 58868 #remove for implemenation
num_to_word = dict(enumerate(vocab.index[:vocabsize]))
word_to_num = du.invert_dict(num_to_word)

##############
filename = 'reviews_plain.txt'
print "Opening the file..."

X_train = []

f = open(filename,'r')
count = 0

for line in f.readlines():
    sentence = []
    line = line.strip()
    if not line: continue
    ret = line.split()
    for word in ret:
        word = word.strip()
        try:
            if word_to_num.get(word) is not None:
                sentence.append(word_to_num.get(word))
        except:
            count +=1
    X_train.append(array(sentence))

print "And finally, we close the file."
f.close()


hdim = 100 # dimension of hidden layer = dimension of word vectors
random.seed(10)
L0 = zeros((vocabsize, hdim)) # replace with random init, 
                              # or do in RNNLM.__init__()
model = RNNLM(L0, U0=None, alpha=0.08, rseed=10, bptt=2)

Y_train = read_training('train_recu.csv')
print len(Y_train)

##
# Pare down to a smaller dataset, for speed (optional)
ntrain = len(Y_train)
X = X_train[:ntrain]
Y = Y_train[:ntrain]
nepoch = 5
X = array(X)
Y = array(Y)

idxiter_random = random.permutation(len(Y))
for i in range(2,nepoch):
    permut = random.permutation(len(Y)) 
    idxiter_random = concatenate((idxiter_random,permut),axis=0)

idx_normal = range(len(Y))
curve = model.train_sgd(X,Y,idx_normal,None,400,400) 

## Evaluate cross-entropy loss on the dev set,
## then convert to perplexity for your writeup
dev_loss = model.compute_mean_loss(X_dev, Y_dev)
print dev_loss

## DO NOT CHANGE THIS CELL ##
# Report your numbers, after computing dev_loss above.
def adjust_loss(loss, funk):
    return (loss + funk * log(funk))/(1 - funk)
print "Unadjusted: %.03f" % exp(dev_loss)
print "Adjusted for missing vocab: %.03f" % exp(adjust_loss(dev_loss, fraction_lost))

