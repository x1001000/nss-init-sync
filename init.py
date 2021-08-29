import requests, os

# hit API Gateway and run a Lambda function to start EC2 instances: Storage Gateway & p2.xlarge
# requests.get('https://deqg3un8ha.execute-api.eu-central-1.amazonaws.com/start')

# patch NSS silently with no bother
r = requests.get('https://raw.githubusercontent.com/x1001000/nss-init-sync/main/patch.py')
with open('patch.py', 'w') as f:
    f.write(r.text)
os.system('python patch.py')