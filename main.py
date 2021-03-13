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
        '--max_slow_poll_interval', required=False, default=600, type=int,
        help='The number of seconds between checking for the file on S3.'
    )
    parser.add_argument(
        '--fast_poll_file', required=False, default='/home/ec2-user/s3_poll_cd.trigger', type=str,
        help='The full path to the file which, when created, immediately triggers a poll'
    )

    args = parser.parse_args()
    poll_continuously(args.s3_bucket, args.s3_key, args.max_slow_poll_interval, args.fast_poll_file)


def poll_continuously(s3_bucket: str, s3_key: str, max_slow_poll_interval: int, fast_poll_file: str):
    max_slow_poll_interval = max(max_slow_poll_interval, 5)

    fast_polls_per_real_poll = 5
    while True:
        for idx in range(fast_polls_per_real_poll):
            if os.path.exists(fast_poll_file):
                print('Fast poll trigger detected!')
                os.unlink(fast_poll_file)
                break
            time.sleep(1)

        print('Polling...')
        if poll(s3_bucket, s3_key):
            print('Executed script')
            fast_polls_per_real_poll = 5
        else:
            fast_polls_per_real_poll = min(fast_polls_per_real_poll + 1, int(max_slow_poll_interval))


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

    cwd = os.getcwd()
    os.system('bash script.sh')
    os.chdir(cwd)
    os.unlink('script.sh')

    s3.delete_object(Bucket=s3_bucket, Key=s3_key)
    return True


if __name__ == '__main__':
    main()
