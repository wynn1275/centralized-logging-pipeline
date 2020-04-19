import unittest
import datetime
import gzip
import json

import boto3


class CentralizedLoggingPocTest(unittest.TestCase):
    kinesis_client = ''
    s3_client = ''
    test_data = []
    expect_data = []

    @classmethod
    def setUpClass(cls) -> None:
        cls.kinesis_client = boto3.client("kinesis", endpoint_url="http://183.111.252.146:4568",
                                          aws_access_key_id="mockaccesskey",
                                          aws_secret_access_key="mocksecretkey",
                                          region_name="us-east-1")
        cls.s3_client = boto3.client('s3', endpoint_url="http://183.111.252.146:4572",
                                     aws_access_key_id="mockaccesskey",
                                     aws_secret_access_key="mocksecretkey",
                                     region_name="us-east-1")
        # set test_data (nginx_access_log)
        test_data_reader = open('example_nginx_access_log.txt', 'r')
        while True:
            line = test_data_reader.readline()
            if not line:
                break
            data = {"message": line}
            record = {"PartitionKey": "test-key", "Data": str(data).encode()}
            cls.test_data.append(record)
        test_data_reader.close()

        # set expect_data
        expect_data_reader = open('expect_data.json', 'r')
        cls.expect_data = json.load(expect_data_reader)
        expect_data_reader.close()

    def test_integration_from_kinesis_stream_to_s3(self):
        # kinesis create event
        kinesis_response = self.kinesis_client.put_records(
            Records=self.test_data,
            StreamName='logging-stream'
        )
        print(str(kinesis_response))
        self.assertEqual(200, kinesis_response['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(4, len(list(kinesis_response['Records'])))
        self.assertEqual(0, kinesis_response['FailedRecordCount'])

        # test s3 - 정상적으로 lambda 가 호출되었으면 s3 에 *.json.gz 파일이 업로드되어야 한다
        s3_response = self.s3_client.list_objects_v2(Bucket="access-log")
        self.assertEqual(200, s3_response['ResponseMetadata']['HTTPStatusCode'])
        s3_key = s3_response['Contents'][-1]['Key']
        self.assertTrue(str(s3_key).startswith(
            datetime.datetime.now(tz=datetime.timezone.utc).strftime('year=%Y/month=%m/day=%d/access_log_')))

        # test s3 - s3 에 업로드된 json 파일의 내용을 검증
        zip_file = "s3_temp_json.gz"
        self.s3_client.download_file("access-log", s3_key, zip_file)
        with gzip.open(zip_file, 'r') as content:
            for idx, line in enumerate(content):
                parsed = json.loads(line)
                self.assertEqual(self.expect_data[idx], parsed)


if __name__ == '__main__':
    unittest.main()
