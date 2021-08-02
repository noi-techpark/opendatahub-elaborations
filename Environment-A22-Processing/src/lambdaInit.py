from dataprocessor.DataProcessor import Processor

f = Processor()

def handleLambdaCall(event,arguments):
    f.calc_by_station()
