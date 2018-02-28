import json
from requests import request, Response

class BlockchainServer:
    _domain = 'localhost'
    _port = 3338

    def transaction(self, user_id:int, candidate_id:int):
        url = f'http://{self._domain}:{self._port}/vote'

        payload = {
            'user_id'       : user_id,
            'candidate_id'  : candidate_id
        }
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        response: Response = request('POST', url, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            return None

