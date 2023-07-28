import math
import requests

class Snipe:
    def __init__(self, url: str, token: str):
        self.url = "{}/api/v1/".format(url if url[-1] != "/" else url[:-1])
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + token,
                        'accept': 'application/json',
                        'content-type': 'application/json'}


    def __get_models(self, session: requests.Session):
        response = session.get(self.url + "models", params={'limit': 100, 'offset': 0},
                               headers=self.headers).json()
        yield response
        num_pages = math.ceil(response['total'] / 100)

        for page in range(1, num_pages):
            next_page = session.get(self.url + "models", params={'limit': 100, 'offset': page * 100},
                                    headers=self.headers).json()
            yield next_page

    def get_via_models(self):
        session = requests.Session()

        fieldsets = self.__get_fieldsets_with_mac(session)
        # print(fieldsets)
        # print(session.get(endpoint + "models", params={'limit': 100, 'offset': 0}, headers=headers).json())

        manufacturers = []
        models = []

        for page in self.__get_models(session):
            for model in page['rows']:
                if model['fieldset'] is not None and model['fieldset']['id'] in fieldsets:
                    # model_name = html.unescape(model['name'])
                    # if model_name not in models:
                    #     models.append(model_name)
                    if model not in models:
                        models.append(model)

                    # manuf_name = html.unescape(model['manufacturer']['name'])
                    # if manuf_name not in manufacturers:
                    #     manufacturers.append(manuf_name)
                    if model['manufacturer'] not in manufacturers:
                        manufacturers.append(model['manufacturer'])

        manufacturers = sorted(manufacturers, key=lambda d: d['id'])
        models = sorted(models, key=lambda d: d['id'])

        # print("manu: ")
        # for manu in manufacturers:
        #     print(manu)
        #
        # print("models: ")
        # for model in models:
        #     print(model)
        return manufacturers, models

    def __get_fieldsets_with_mac(self, session: requests.Session):
        response = session.get(self.url + "fieldsets", headers=self.headers).json()
        fieldsets_with_mac = []

        for fieldset in response['rows']:
            for fields in fieldset['fields']['rows']:
                if str(fields['format']).lower() == "mac":
                    fieldsets_with_mac.append(fieldset['id'])
                    break

        return fieldsets_with_mac

    def get_companies(self):
        session = requests.Session()
        return session.get(self.url + "companies", headers=self.headers).json()['rows']
