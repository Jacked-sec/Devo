import time
import hmac
import hashlib
import json

api_key = 'xxxxx'
api_secret = 'xxxxx'
timestamp = str(int(time.time()) * 1000)

# Convert the data to a JSON string (Creates a new domain)
data1 = json.dumps({"name": "xxxx@xxxx", "plan": "gable_children"})

# Adds an internal user
data2 = json.dumps({"domain": "xxxx@xxxx","userName": "xxxx xxxx","email": "xxxx@xxxx.com","role": "Owner"})

# Create the signature(Creates a new domain)
sign1 = hmac.new(bytes(api_secret, 'utf-8'), bytes(api_key + data1 + timestamp, 'utf-8'), hashlib.sha256)
sign1 = sign1.hexdigest()

# Create the signature(Creates a new user)
sign2 = hmac.new(bytes(api_secret, 'utf-8'), bytes(api_key + data2 + timestamp, 'utf-8'), hashlib.sha256)
sign2 = sign2.hexdigest()



print("Creates a new domain")
print("x-logtrust-sign =",sign1)
print("x-logtrust-timestamp =",timestamp)
print(data1)
print("Creates a new user")
print("x-logtrust-sign =",sign2)
print("x-logtrust-timestamp =",timestamp)
print(data2)

#Use in - > https://api-apac.devo.com/probio/apiDoc/index.html#/reseller/post_domain