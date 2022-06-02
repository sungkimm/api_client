import aiohttp
import asyncio
import time
import requests
import uvloop
import abc, os


class AioHTTPClientTemplate(abc.ABC):

    def __init__(self, base_url, req_method, connection_limit=0):
        
        self.base_url = base_url
        if req_method not in ['get', 'post', 'put', 'delete']:
            raise Exception("Invalid request method")
        self.req_method = req_method
        self.connection_limit = connection_limit  # 0 = unlimited

        # set uvloop as a default loop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


    @abc.abstractmethod
    def create_metadata_to_send(self, is_sync_req=False, **kwarg):
        '''
        Create path, query, form, body, etc data in a dictionary form to send with.
        This data will either pass to session(aiohttp) or requests module depending on is_sync_req option
        aiohttp session.get() and requests.get() takes different paramater in different manner, 
        so make sure to define both if you willing to test synchronous request with requests module.
        '''
        pass


    @abc.abstractmethod
    async def send_request(self, **kwarg):
        '''
        Make corutine to request and await the responses
        '''
        pass


    @abc.abstractmethod
    def create_request_loop(self, **kwarg):
        '''
        Iterate number of requests to send and yield parameters in dictionary to pass to send_request()
        '''
        pass

    
    def set_session_call(self):
        '''
        Add HTTP method to an aiohttp client session
        '''
        self.session_call = eval("self.session."+ self.req_method)

    def single_asynchronous_request(self, **kwarg):
        '''
        asynchronous requests
        This function must takes the same paramters defined in create_metadata_to_send()
        '''
        session_call = eval("requests."+ self.req_method)
        response = session_call(**self.create_metadata_to_send(is_sync_req=True, **kwarg))
        print(response.json())
        
        
    def multi_asynchronous_request(self):
        for params in self.create_request_loop():
            self.single_asynchronous_request(**params)



    async def async_loop_chunck(self, **kwarg):
        
        uv_loop = asyncio.get_event_loop()
        
        conn = aiohttp.TCPConnector(limit=self.connection_limit, loop=uv_loop)
        async with aiohttp.ClientSession(connector=conn) as self.session: # make sure to use a single session
            self.set_session_call() # ex) self.session.get or post

            tasks = []
            for params in self.create_request_loop():
                tasks.append(self.send_request(**params))

            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            print("----- Total API response took {:0.4f} seconds -----".format(time.time() - start_time))

        
        return responses

    def run_async_request(self, **kwarg):
        ''' run the async job'''
        
        start_time = time.time()
        results = asyncio.run(self.async_loop_chunck(**kwarg))
        print("----- The entire program took {:0.4f} seconds -----".format(time.time() - start_time))

        return results


class SimpleAioHTTPClientExample(AioHTTPClientTemplate):
    '''
    An example on how to aiohttp request using AioHTTPClientTemplate

    Simply sending a request to a given url adding parameter to path(url)
    
    server side : http://blahblah:port/path/param (get)
    '''

    def __init__(self, base_url, req_method, n_task):
        super().__init__(base_url, req_method)
        self.n_task =  n_task


    def create_metadata_to_send(self, idx, is_sync_req=False):

        url = '{}{}'.format(self.base_url, idx)
        return {"url" : url}


    async def send_request(self, **kwarg):
        
        # async with self.session.get(**self.create_metadata_to_send(**kwarg)) as response:
        async with self.session_call(**self.create_metadata_to_send(**kwarg)) as response:
            rst = await response.json()
            if response.status != 200:
                print(rst)
            return rst
    
    def create_request_loop(self, **kwarg):

        for i in range(1, self.n_task):
            yield {'idx' : i}



class AudioAioHTTPClient(AioHTTPClientTemplate):
    '''
    Audio file aiohttp request example
    This example pass audio file and text with special key added to headers
    '''

    def __init__(self, base_url, req_method, file_path):
        super().__init__(base_url, req_method)
        self.file_path =  file_path
        self.headers = {'auth-key': 'blahblah'}


    def create_metadata_to_send(self, audio_path, txt_path, is_sync_req=False):

        # read text file
        with open(txt_path, 'r') as txt_file:
            text = txt_file.read().strip()
        
        # create form-data
        if not is_sync_req:
            files = {"audio": open(audio_path,'rb'), "text": text}
            params = {'url': self.base_url, "data" : files, "headers" :self.headers}
        else:
            files = {"audio": open(audio_path,'rb')}
            data = {"text": text}
            params = {'url': self.base_url, "files" : files, "data": data, "headers" :self.headers}

        return params


    async def send_request(self, **kwarg):
        
        # async with self.session.get(**self.create_metadata_to_send(**kwarg)) as response:
        async with self.session_call(**self.create_metadata_to_send(**kwarg)) as response:
            rst = await response.json()
            print(rst)
            return rst

    
    
    def create_request_loop(self, **kwarg):
        from glob import glob

        for audio_path in glob(os.path.join(self.file_path, '*.wav')):
            base_dir = os.path.dirname(audio_path)
            txt_filename = os.path.basename(audio_path).split('.')[0]+'.txt'
            txt_path = os.path.join(base_dir,txt_filename)
            
            yield {'audio_path' : audio_path, 'txt_path' : txt_path}


if __name__ == '__main__':


    # n_task = 10
    # base_url = 'http://localhost:6001/async/'
    
    # simple_aiohttp = SimpleAioHTTPClientExample(base_url, "get", n_task)
    # response_results = simple_aiohttp.run_async_request()
    
    # simple_aiohttp.single_asynchronous_request(idx =1)
    # simple_aiohttp.multi_asynchronous_request()

    
    base_url = "http://34.64.70.78:8999/aligner"
    base_url = "http://222.236.44.83:8999/aligner"
    
    file_path = "/Users/sungkim/Downloads/eng"
    audio_aiohttp = AudioAioHTTPClient(base_url, "post", file_path)
    audio_aiohttp.run_async_request()

    # audio_path = "/Users/sungkim/Downloads/eng/0b70f50e-c8ba-418a-b2ba-95547f420484.wav"
    # txt_path = "/Users/sungkim/Downloads/eng/0b70f50e-c8ba-418a-b2ba-95547f420484.txt"
    # audio_aiohttp.single_asynchronous_request(audio_path=audio_path, txt_path=txt_path)
    # audio_aiohttp.multi_asynchronous_request()


    