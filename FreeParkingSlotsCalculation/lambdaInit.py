from calculateFreeParkingSlots import FreeParkingSlotsCalculator

f = FreeParkingSlotsCalculator()

def handleLambdaCall(event,arguments):
    f.startCalculations()
