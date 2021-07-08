from dataProcessor import DataProcessor

f = DataProcessor()

def handleLambdaCall(event,arguments):
    f.startCalculations()
