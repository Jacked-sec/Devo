import time
import hmac
import hashlib
import json

api_key = '9kC4KPvx18KtX4VFhhPTTLTZH51rGPdsPUuwbwpwR1Kcg308es'
api_secret = 'jYk56wv6xIAeTNi2nQTTzRm5z2CVNKp3zyMizxh8lXB04lD8oPyudvVChtnao3xb'
timestamp = str(int(time.time()) * 1000)

# Convert the data to a JSON string (Creates a new domain)
data1 = json.dumps({"name": "Chandler@gable", "plan": "gable_children"})

# Adds an internal user
data2 = json.dumps({"domain": "Chandler@gable","userName": "Tanakong Chujai","email": "tanakong.c@g-able.com","role": "Owner"})

# Create the signature(Creates a new domain)
sign1 = hmac.new(bytes(api_secret, 'utf-8'), bytes(api_key + data1 + timestamp, 'utf-8'), hashlib.sha256)
sign1 = sign1.hexdigest()

# Create the signature(Creates a new user)
sign2 = hmac.new(bytes(api_secret, 'utf-8'), bytes(api_key + data2 + timestamp, 'utf-8'), hashlib.sha256)
sign2 = sign2.hexdigest()



print("Creates a new domain")
print(sign1)
print(timestamp)
print(data1)
print("Creates a new user")
print(sign2)
print(timestamp)
print(data2)

#Use in - > https://api-apac.devo.com/probio/apiDoc/index.html#/reseller/post_domain