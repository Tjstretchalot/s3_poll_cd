import boto3
import botocore.exceptions
import os
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description='Poll s3 for a script to execute then delete the file')
    parser.add_argument(
        '--s3_bucket', required=True,
        help='The S3 Bucket where the script to poll is located'
    )
    parser.add_argument(
        '--s3_key', required=True,
        help='The key within the bucket where the script is located'
    )
    parser.add_argument(
        '--poll_interval', required=False, default=300, type=int,
        help='The number of seconds between checking for the file'
    )

    args = parser.parse_args()
    poll_continuously(args.s3_bucket, args.s3_key, args.poll_interval)


def poll_continuously(s3_bucket: str, s3_key: str, poll_interval: int):
    actual_poll_interval = min(poll_interval, 5)
    while True:
        print('Polling...')
        if poll(s3_bucket, s3_key):
            print('Executed script')
            actual_poll_interval = min(poll_interval, 5)
        else:
            actual_poll_interval = min(poll_interval, actual_poll_interval + 5)

        time.sleep(actual_poll_interval)


def poll(s3_bucket: str, s3_key: str):
    s3 = boto3.client('s3')
    try:
        s3.download_file(s3_bucket, s3_key, 'script.sh')
    except botocore.exceptions.ClientError as e:
        code = int(e.response.get('Error', {}).get('Code', '-1'))
        if code == 404:
            # not found
            return False
        raise e

    os.system('script.sh')
    os.unlink('script.sh')

    s3.delete_object(Bucket=s3_bucket, Key=s3_key)
    return True


if __name__ == '__main__':
    main()
