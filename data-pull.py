import json
import urllib3


# All the relevant Human API endpoints 
# (cf. https://reference.humanapi.co/reference/wellness-api-introduction)
# Excludes profile, meals and human
wellness_endpoints = [
	"/v1/human/activities",
	"/v1/human/activities/summaries",
	"/v1/human/blood_glucose",
	"/v1/human/blood_oxygen",
	"/v1/human/blood_pressure",
	"/v1/human/bmi",
	"/v1/human/body_fat",
	"/v1/human/heart_rate",
	"/v1/human/heart_rate/summaries",
	"/v1/human/height"
	]


def get_access_token(clientId, clientSecret, clientUserId):
	http = urllib3.PoolManager()
	data = json.dumps({ 
		"client_id": clientId, 
		"client_secret" : clientSecret , 
		"client_user_id" : clientUserId, 
		"type" : "access"
	})
	r = http.request(
	    'POST',
	    'https://auth.humanapi.co/v1/connect/token',
	    body=data,
	    headers={'Content-Type': 'application/json'}
	)
	if r.status >= 400:
		raise Exception("Error while retrieving Human API access token")
	else:
		return json.loads(r.data.decode("utf-8"))



def get_feed(accessToken, endpoint, offset = 0):
	http = urllib3.PoolManager()
	r = http.request(
	    'GET',
	    'https://api.humanapi.co'+endpoint+"?offset="+str(offset),
	    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer '+accessToken}
	)
	if r.status >= 400:
		raise Exception("Error while retrieving data from Human API "+endpoint,r.status)
	else:
		data = json.loads(r.data.decode("utf-8"))
		cursor = len(data)+offset
		if "X-Total-Count" in r.headers:
			totalCount = int(r.headers["X-Total-Count"])
		else:
			totalCount = 0

		# we're not done yet. Get the next one and returned a concatenated list
		if offset+len(data) < totalCount:
			return data+get_feed(accessToken,endpoint,cursor)
		else:
			return data



access_token = get_access_token(
		"--your clientid --",
		"--your client secret--",
		"--the user unique identifier"
	)

## Builds a dictionary where keys are the endpoints and values are arrays
## of datapoints
data = dict()
for endpoint in wellness_endpoints:
	print("Retrieving data from ",endpoint)
	data[endpoint] = get_feed(access_token["access_token"],endpoint)

## Writes the data into a JSON file
fd = open("humanapi-wellness-data.json","w")
fd.write(json.dumps(data))
fd.close()


