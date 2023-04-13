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
        self.test_size = int(3*self.train_size/5)

        # transform data
        # self.data['Time'] = self.data.apply(lambda x: pd.Timestamp.round(
        #                     pd.to_datetime(
        #                         x['MillisFromMidn'],
        #                         unit = 'ms',
        #                         origin=str(x.Date)),
        #                     freq = '5T'),
        #                 axis = 1
        # )
        # self.data = (self.data
        #     .pivot_table(values = 'Returns',index = ['Time'],columns = 'Ticker')
        #     .reset_index()
        #     .sort_values(by = ['Time'],ignore_index=True)
        # )
        
        
    
    def get_n(self):
        # self.n = (len(self.data)-self.train_size)//self.test_size
        self.n = len(self.test)
        return self.n

    def split(self):
        t_tol = len(self.data)
        test_start_index = list(range(t_tol-self.test_size,self.train_size-1,-self.test_size))
        test_start_index.reverse()
        train_start_index = [i-self.train_size for i in test_start_index]
        self.train = {i:list(range(train_start_index[i],train_start_index[i]+self.train_size)) 
                    for i in range(len(train_start_index))}
        self.test = {i:list(range(test_start_index[i],test_start_index[i]+self.test_size)) 
                    for i in range(len(test_start_index))}
       
    def get_train_index(self,fold=None):
        # return a list of train set index at specified fold; if None, return all fold
        # example: return [[1,2,3][4,5,6]] when fold = [1,2]
        if fold == None:
            return self.train
        else:
            return [self.tain[k] for k in fold]

    def get_test_index(self,fold=None):
        #similar to get_train_index
        if fold == None:
            return self.test
        else:
            return [self.test[k] for k in fold]


    def get_train_set(self,fold=None):
        
        if fold==None:
            return self.data
        return self.data.iloc[self.train[fold]]

    def get_test_set(self,fold=None):
        
        if fold==None:
            return self.data
        return self.data.iloc[self.test[fold]]


    