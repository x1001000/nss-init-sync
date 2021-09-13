import os, sys, requests

# hit API Gateway and run a Lambda function to start EC2 instances: Storage Gateway & p2.xlarge
site = sys.argv[1]
payload = {'site': site}
requests.get(sys.argv[2], params=payload)

# patch NSS silently with no bother
with requests.get(sys.argv[3]) as r:
    with open(os.path.join(os.getcwd(), 'patch.py'), 'w') as f:
        f.write(r.text)
os.system(f"python {os.path.join(os.getcwd(), 'patch.py')}")

# renew
with open(os.path.join(os.getcwd(), 'upload_progress.ns'), 'w') as up:
        up.write('...')