import unittest

from ODHAPIClient import DataFetcher


odh_client = DataFetcher()
class TestFetch(unittest.TestCase):
    def test_fetch_data(self):
        data = odh_client.fetch_data("/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.3600&select=mvalidtime,scode&limit=-1")
        self.assertEquals(data['offset'],0)
        
    def test_fetch_newest_elaborations(self):
        data = odh_client.get_newest_data_timestamps()

    def test_get_raw_history(self):
        data = odh_client.get_raw_history('AUGEG4_AIRQ06','2021-06-06 00:00:00.000+0000','2021-06-06 10:00:00.000+0000')

if __name__ == '__main__':
    unittest.main()

