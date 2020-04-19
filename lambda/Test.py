import base64
import json
import unittest

import access_log_parser


class ParseTestCase(unittest.TestCase):
    test_data = {}

    @classmethod
    def setUpClass(cls) -> None:
        test_data_reader = open('example_kinesis_stream.json', 'r')
        cls.test_data = json.load(test_data_reader)
        test_data_reader.close()

    def test_parse_log_success(self):
        for i, record in enumerate(self.test_data['Records']):
            payload = base64.b64decode(record['kinesis']['data'])
            log = json.loads(payload)
            if 'message' in log:
                parsed = access_log_parser.parse_log(log['message'])
                print(parsed)
                self.assertEqual(assert_data[i], parsed)


if __name__ == '__main__':
    test_data = open('example_kinesis_stream.json', 'r')
    unittest.main()

assert_data = [
    {'remote': '112.168.224.198', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:07:59 +0000', 'method': 'GET',
     'path': '/ ', 'code': '200', 'size': '3184',
     'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'},
    {'remote': '185.2.196.196', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:08:00 +0000', 'method': 'GET',
     'path': '/ ', 'code': '200', 'size': '3184',
     'agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'},
    {'remote': '112.168.224.198', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:08:01 +0000', 'method': 'GET',
     'path': '/ipfiltersimulation-20200408124128699/ ', 'code': '200', 'size': '35892',
     'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'},
    {'remote': '112.168.224.198', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:08:01 +0000', 'method': 'GET',
     'path': '/ipfiltersimulation-20200408124128699/js/jquery.min.js ', 'code': '200', 'size': '93637',
     'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'},
    {'remote': '112.168.224.198', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:08:01 +0000', 'method': 'GET',
     'path': '/ipfiltersimulation-20200408124128699/js/bootstrap.min.js ', 'code': '200', 'size': '5569',
     'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'},
    {'remote': '112.168.224.198', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:08:01 +0000', 'method': 'GET',
     'path': '/ipfiltersimulation-20200408124128699/js/gatling.js ', 'code': '200', 'size': '3690',
     'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'},
    {'remote': '112.168.224.198', 'host': '-', 'user': '-', 'datetime': '19/Apr/2020:04:08:01 +0000', 'method': 'GET',
     'path': '/ipfiltersimulation-20200408124128699/js/menu.js ', 'code': '200', 'size': '2655',
     'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}
]
