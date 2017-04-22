import  pandas as pd
from sklearn.svm import  SVC

def classifier(label):
    "returns list of songs in that class"
    #LOAD train and test
    train = pd.read_csv("main2.csv",header= None)
    test = pd.read_csv("storage.csv",header=None)
    #Train the SVC
    model = SVC(kernel="linear")
    model.fit(train.iloc[:,1:-1],train.iloc[:,-1])
    #Update The list
    result = []
    for i in range(test.shape[0]):
             if model.predict([test.iloc[i,1:-1]])[0] == label:
                k = []
                k.append(test.iloc[i,0])
                k.append(label)
                result.append(k)
    return result

#Call with a class label and watch the magic


def smain():
    k = []
    for i in range(0,14):
        for j in classifier(i):
            k.append(j)
    return k