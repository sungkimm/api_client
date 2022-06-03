import requests
import uvloop
import asyncio, aiohttp
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

'''
audio request example on requests and aiohttp module
scenario: server takes wav audio file and text in a form-data format with post http method with specific header key and value
requests module and aiohttp take metadata parameters in a different way.
check the code below
'''

def audio_sync_request(**params):
    # result = requests.post(url, files=files, data=data, headers=headers, timeout=None)
    result = requests.post(**params)
    print(result.json())



async def aiohttp_request(**params):

    vloop = asyncio.get_event_loop()
    conn = aiohttp.TCPConnector(limit=0, loop=vloop)

    async with aiohttp.ClientSession(connector=conn) as session: # make sure to use a single session
        async with session.post(**params) as resp:
            rst = await resp.json()
            print(rst)
    
    return rst



if __name__ == '__main__':

    url = "http://222.236.44.83:8999/aligner"
    audio_path = '/Users/sungkim/Downloads/eng/0b70f50e-c8ba-418a-b2ba-95547f420484.wav'
    text_message = 'test text message'
    auth_key = "blahblah"

    

    ########## sync request with request module ############
    files = {"audio":  open(audio_path,'rb')}
    data = {"text": text_message}
    headers = {'auth-key': auth_key}

    sync_params = {"url" : url,
                    "files": files,
                    "data": data,
                    "headers": headers}

    audio_sync_request(**sync_params)



    ############ async parameter with aiohttp ################
    data = {"audio":  open(audio_path,'rb'), "text": text_message}
    headers = {'auth-key': auth_key}

    async_aio_params = {"url" : url,
                        "data": data,
                        "headers": headers}
    

    asyncio.run(aiohttp_request(**async_aio_params))
    

