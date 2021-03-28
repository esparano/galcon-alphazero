import matplotlib.pyplot as plt 
    
def plotNNTrainingSession(session):
    plt.figure(1, figsize=(18, 18))

    # summarize history for accuracy  

    plt.subplot(211)  
    # plt.plot(history.history['policy_acc'])  
    plt.plot(session.historyPolicyValAcc)  
    # plt.plot(history.history['value_acc'])  
    plt.plot(session.historyValueValAcc)  
    plt.title('model accuracy')  
    plt.ylabel('accuracy')  
    plt.xlabel('epoch')  
    # plt.legend(['policy_categorical_accuracy', 'val_policy_categorical_accuracy', 'value_categorical_accuracy', 'val_value_categorical_accuracy'], loc='upper left')  
    plt.legend(['Validation Policy Accuracy','Validation Value Accuracy'], loc='upper left')  

    # summarize history for loss  

    plt.subplot(212)  
    plt.plot(session.historyPolicyValLoss)  
    plt.plot([x * 10 for x in session.historyValueValLoss])  
    plt.plot(session.historyValLoss)   
    plt.title('model loss')  
    plt.ylabel('loss')  
    plt.xlabel('epoch')  
    # plt.legend(['policy_loss', 'val_policy_loss', 'value_loss','val_value_loss','loss','val_loss',], loc='upper left')  
    plt.legend(['val_policy_loss','val_value_loss','val_loss'], loc='upper left')  

    plt.savefig('recentPlot.png')

    plt.show()  

