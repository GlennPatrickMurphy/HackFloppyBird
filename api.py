
import requests
import json


class Api:

    def __init__(self, payload, key):
        self.url = 'https:/#####@scalr.api.appbase.io/sv_instructor/'
        url = self.url + "_bulk"
        payload = "{ \"index\": { \"_type\": \"users\", \"_id\": \"" + key + "\" } }\n" \
                  "{ \"name\": \"" + str(payload['name']) + "\"," \
                  "\"email\":\"" + str(payload['email']) + "\"," \
                  "\"school\":\"" + str(payload['school']) + "\"," \
                  "\"phone_number\": \"" + str(payload['phone_number']) + "\"," \
                  "\"first_score\":\"" + str(payload['first_score']) + "\"," \
                  "\"second_score\":\"" + str(payload['second_score']) + "\"}\n"

        response = requests.request('POST', url, data=payload.encode('utf-8'), allow_redirects=False)

        csvfile = open("FlappyCSV.txt", 'a')
        csvfile.write(payload)
        csvfile.close()

        try:
            print(response.json())
        except json.decoder.JSONDecodeError:
            return
