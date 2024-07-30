import aiohttp


class StalcraftAPI:
    def __init__(self, client_id, client_secret, url="https://eapi.stalcraft.net/",
                 debug=False,
                 stalcraft_status_key=None,
                 stalcraft_status_url='https://stalcraft-status.ru/',
                 demo_url='https://dapi.stalcraft.net/',
                 ):
        self.__api_url = url if not debug else demo_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.debug = debug
        self.stalcraft_status_key = stalcraft_status_key
        self.stalcraft_status_url = stalcraft_status_url
        self.appToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwibmJmIjoxNjczNzk3ODM4LCJleHAiOjQ4MjczOTc4MzgsImlhdCI6MTY3Mzc5NzgzOCwianRpIjoiYXhwbzAzenJwZWxkMHY5dDgzdzc1N2x6ajl1MmdyeHVodXVlb2xsZ3M2dml1YjVva3NwZTJ3eGFrdjJ1eWZxaDU5ZDE2ZTNlN2FqdW16Z3gifQ.ZNSsvwAX72xT5BzLqqYABuH2FGbOlfiXMK5aYO1H5llG51ZjcPvOYBDRR4HUoPZVLFY8jyFUsEXNM7SYz8qL9ePmLjJl6pib8FEtqVPmf9ldXvKkbaaaSp4KkJzsIEMY_Z5PejB2Vr-q-cL13KPgnLGUaSW-2X_sHPN7VZJNMjRgjw4mPiRZTe4CEpQq0BEcPrG6OLtU5qlZ6mLDJBjN2xtK0DI6xgmYriw_5qW1mj1nqF_ewtUiQ1KTVhDgXnaNUdkGsggAGqyicTei0td6DTKtnl3noD5VkipWn_CwSqb2Mhm16I9BPfX_d5ARzWrnrwPRUf6PA_7LipNU6KkkW0mhZfmwEPTm_sXPus0mHPENoVZArdFT3L5sOYBcpqwvVIEtxRUTdcsKp-y-gSzao5muoyPVoCc2LEeHEWx0cIi9spsZ46SPRQpN4baVFp7y5rp5pjRsBKHQYUJ0lTmh1_vyfzOzbtNN2v6W_5w9JTLrN1U6fhmifvKHppFSEqD6DameL1TC59kpIdufRkEU9HE4O-ErEf1GuJFRx-Dew6XDvb_ExhvEqcw31yNvKzpVqLYJfLazqn6tUbVuAiPwpy6rP9tYO2taT1vj5TGn_vxwDu9zoLWe796tFMPS-kmbCglxB5C9L4EbpfWNbWxYjUkTvjT2Ml9OnrB0UbYo1jI'
        self.authHeader = {"Authorization": f"Bearer {self.appToken}"}
        self.session = aiohttp.ClientSession()


    async def __request_get(self, endpoint, headers=None, apiUrl=None, method='get'):
        apiUrl = apiUrl if apiUrl else self.__api_url
        url = apiUrl + endpoint
        if method == 'post':
            async with self.session.post(url, data=headers) as resp:
                r = await resp.json()
        else:
            async with self.session.get(url, headers=headers) as resp:
                r = await resp.json()
        return r
    
    #No stalcraft api
    async def get_stalcraft_online(self):
        if not self.stalcraft_status_key:
            return 0
        try:
            endpoint = 'api/v1/last'
            params = f'?token={self.stalcraft_status_key}&v=2'
            endpoint += params
            r = await self.__request_get(endpoint, apiUrl=self.stalcraft_status_url)
            return int(r.get('online'))
        except Exception as e:
            print(e)
            return 0
    
    async def get_regions(self):
        endpoint = 'regions'
        r = await self.__request_get(endpoint, self.authHeader)
        return r

    async def get_auction_history(self, item_id, region, additional="true", limit=100, offset=0):
        endpoint = f'{region}/auction/{item_id}/history'
        params = f'?limit={limit}&additional={additional}&offset={offset}'
        endpoint += params
        r = await self.__request_get(endpoint, self.authHeader)
        return r

    async def get_auction_lots(self, item_id, region, additional="true",
                               limit=20, offset=0, select="buyout_price", order=True):
        if order:
            sorder = "asc"
        else:
            sorder = "desc"
        endpoint = f'{region}/auction/{item_id}/lots'
        params = f'?limit={limit}&sort={select}&offset={offset}&order={sorder}&additional={additional}'
        endpoint += params
        r = await self.__request_get(endpoint, self.authHeader)
        return r

    async def get_emission(self, region):
        endpoint = f'{region}/emission'
        r = await self.__request_get(endpoint, self.authHeader)
        return r

    async def run(self):
        if self.debug:
            return True
        endpoint = 'oauth/token'
        headers = {
            "client_id": str(self.client_id),
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        r = await self.__request_get(endpoint, headers, apiUrl='https://exbo.net/', method='post')
        self.appToken = r.get('access_token')
        self.authHeader = {"Authorization": f"Bearer {self.appToken}"}
        return r

    async def close(self):
        await self.session.close()
