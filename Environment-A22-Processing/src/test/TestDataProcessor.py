import unittest

from dataprocessor.DataProcessor import Processor


processor = Processor()
class TestDataProcessor(unittest.TestCase):
    def test_calc_by_station(self):
        processor.calc_by_station()
    """def test_processing_of_no2(self):
        controlUnitId = "AIRQ01"
        data = {
            "NO2" : 5,
            "temperature-internal" : 11.4,
            "O3":21.32,
            "RH":2,
            "PM10":1.32,
            "PM2.5":10
        }
        processed = processor.calc_single_time(data, controlUnitId, "2021-01-01 10:00:00.0001+0000")"""
if __name__ == '__main__':
    unittest.main()

