def getXAxisReflectedTrainingData(data):
    data = data.copy()
    for sample in data:
        for row in sample:
            row[8] *= -1
            row[11] *= -1
            row[14] *= -1
    return data

def getYAxisReflectedTrainingData(data):
    pass #TODO: IMPLEMENT ME