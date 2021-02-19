# S3 Poll Continuous Deployment

This is another technique for continuous deployment that works by
polling for S3 files and, when they are detected, downloading them
and running them as shell scripts.

This is meant to add as alternative way to interface with GitHub
compared to directly receiving webhooks, like CodePipeline, which
avoids the need to have an open port specifically for this deploy.

The expected flow using this technique is

GitHub Actions -> Bundle, S3 Write
Target Instance -> S3 Poll -> S3 Download -> Execute -> S3 Delete

So long as the S3 bucket is completely private, i.e., GitHub actions
and the instance are both using authenticated and encrypted requests
to S3, this should not pose a serious security risk. However, the
general method is essentially the same as command and control servers,
so do your own analysis.

## Authenticating

This library expects a standard s3 authentication file is in place, or
standard environment variables are in place.

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration

## Arguments

- `--s3_bucket`: The name of the S3 bucket the file is in, e.g., `mybucket`
- `--s3_key`: The path to the file within s3, e.g., `deploys/i-1234/runner.sh`
- `--poll_interval`: Max time between polls for changes, in seconds. Defaults
  to 300.

## Running

```sh
git clone --depth 1 https://github.com/tjstretchalot/s3_poll_cd.git
cd s3_poll_cd
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
screen -dmS s3_poll_cd ./run.sh
```
