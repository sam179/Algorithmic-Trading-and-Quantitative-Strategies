import pandas as pd
from MyDirectories import *

class TrainTestSplit():
    '''
    class to perform train test split
    '''
    filePath = MyDirectories.BASE_DIR

    def __init__(self,filename,q=.5):
        self.data = pd.read_csv(self.filePath/filename,index_col=[0])
        self.q = q
        self.train = {} # will be a dictionary K:1,2,3...fold number; V:index of train of that fold
        self.test = {} # same as self.train
        self.train_size = int(500/self.q) #size for each train set
        self.test_size = 78

        
        
        
    
    def get_n(self):
        'Get the number of folds after split'
        self.n = len(self.test)
        return self.n

    def split(self):
        t_tol = len(self.data)
        if t_tol<self.train_size+self.test_size:
            print('Total length is too small to split!')
            return 
        test_start_index = list(range(t_tol-self.test_size,self.train_size-1,-self.test_size))
        test_start_index.reverse()
        train_start_index = [i-self.train_size for i in test_start_index]
        self.train = {i:list(range(train_start_index[i],train_start_index[i]+self.train_size)) 
                    for i in range(len(train_start_index))}
        self.test = {i:list(range(test_start_index[i],test_start_index[i]+self.test_size)) 
                    for i in range(len(test_start_index))}
       


    def get_train_set(self,fold=None):
        
        if fold==None:
            return self.data
        return self.data.iloc[self.train[fold]]

    def get_test_set(self,fold=None):
        
        if fold==None:
            return self.data
        return self.data.iloc[self.test[fold]]


    