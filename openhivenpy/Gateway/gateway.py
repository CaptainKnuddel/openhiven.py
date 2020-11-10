import requests
import websockets
import asyncio
import json
import time
import sys
import json
import datetime
import logging
from typing import Optional

import openhivenpy.Types as types
import openhivenpy.Exception as errs
import openhivenpy.Utils as utils

logger = logging.getLogger(__name__)


class API():
    """`openhivenpy.Gateway`
    
    API
    ~~~
    
    API Class for interaction with the Hiven API
    
    
    """
    def __init__(self):
        self.api_url = "https://api.hiven.io/v1"
    
    # Gets a json file from the hiven api
    async def get(self, keyword: str = "", headers={'content_type': 'application/json'}) -> dict:
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp

    # Sends a request to the API. Mostly so I dont have to auth 24/7.
    async def api(self, method: str, endpoint: str, body):
        resp = None
        headers = {"content_type": "application/json","authorization": self._TOKEN}
        if method == "get":
            resp = requests.get(f"{self.api_url}/{endpoint}",headers=headers,data=body)
        elif method == "post":
            resp = requests.post(f"{self.api_url}/{endpoint}",headers=headers,data=body)
        elif method == "patch":
            resp = requests.patch(f"{self.api_url}/{endpoint}",headers=headers,data=body)
        elif method == "delete":
            resp = requests.delete(f"{self.api_url}/{endpoint}",headers=headers,data=body)

        return resp

class Websocket(API):
    """`openhivenpy.Gateway`
    
    Websocket
    ~~~~~~~~~
    
    Websocket Class that will listen to the Hiven Websocket and trigger user-specified events.
    
    Calls `openhivenpy.Events` and will execute the user code if registered
    
    Parameter:
    ----------
    
    
    """    
    def __init__(self, api_url: str, api_version: str, token: str, heartbeat: int or float, ping_timeout: int, 
                 close_timeout: int, ping_interval: int, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop()):
        
        self._api_url = api_url
        self._api_version = api_version

        self._WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self._ENCODING = "json"

        # Heartbeat is the interval where messages are going to get sent. 
        # In miliseconds
        self._HEARTBEAT = heartbeat

        self._connection_status = "closed"

        self._open = False
        self._closed = True

        self._connection_start = None
        self._startup_time = None
        
        self._ping_timeout = ping_timeout
        self._close_timeout = close_timeout
        self._ping_interval = ping_interval
        
        self._event_loop = event_loop
        asyncio.set_event_loop(self._event_loop)

        if not hasattr(self, '_CUSTOM_HEARBEAT'):
            logger.critical("The client attribute _CUSTOM_HEARTBEAT does not exist! The class is likely faulty initialized!")
            raise errs.FaultyInitialization("The client attribute _CUSTOM_HEARTBEAT does not exist! The class is likely faulty initialized!")


    @property
    def ping_timeout(self) -> int:
        return self._ping_timeout

    @property
    def close_timeout(self) -> int:
        return self._close_timeout

    @property
    def ping_interval(self) -> int:
        return self._ping_interval

    @property
    def api_url(self) -> str:
        return self._api_url

    @property
    def api_version(self) -> str:
        return self._api_version

    @property
    def websocket_url(self) -> str:
        return self._WEBSOCKET_URL

    @property
    def encoding(self) -> str:
        return self._ENCODING

    @property
    def heartbeat(self) -> int:
        return self._HEARTBEAT

    @property
    def connection_status(self) -> str:
        return self._connection_status

    # Simple async function for getting the connection_status
    async def get_connection_status(self) -> str:
        """
            Simple async function for getting the connection_status
            
            Retursn the `str`: connection_status
        """
        return self.connection_status

    @property
    def open(self) -> bool:
        return self._open

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def websocket(self) -> websockets.client.WebSocketClientProtocol:
        """
        
        Returns the ReadOnly Websocket with it's configuration
        
        """    
        return self._websocket

    @property
    def initalized(self) -> bool:
        return self._initalized

    @property
    def connection_start(self) -> float:
        return self._connection_start

    @property
    def startup_time(self) -> float:
        return self._startup_time


    # Starts the connection over a new websocket
    async def create_connection(self, heartbeat: int or float = None) -> None:
        """
        
        Creates a connection to the Hiven API. Not supposed to be called by the user! Rather use HivenClient.connect() or HivenClient.run()
        
        """        

        self._HEARTBEAT = heartbeat if heartbeat != None else self._HEARTBEAT

        async def websocket_connect() -> None:
            try:
                # Connection Start variable for later calculation the time how long it took to start
                self._connection_start = time.time()

                async with websockets.connect(uri = self._WEBSOCKET_URL, ping_timeout = self._ping_timeout, 
                                              close_timeout = self._close_timeout, ping_interval = self._ping_interval) as websocket:

                    websocket = await self.websocket_init(websocket)

                    # Authorizing with token
                    logger.info("Logging in with token")
                    await websocket.send(json.dumps( {"op": 2, "d": {"token": str(self._TOKEN)} } ))

                    # Receiving the first response from Hiven and setting the specified heartbeat
                    response = json.loads(await websocket.recv())
                    if response['op'] == 1 and self._CUSTOM_HEARBEAT == False:
                        self._HEARTBEAT = response['d']['hbt_int']
                        logger.debug(f"Heartbeat set to {response['d']['hbt_int']}")
                        websocket.heartbeat = self._HEARTBEAT

                    self._closed = websocket.closed
                    self._open = websocket.open

                    # Triggering the user event for the connection start
                    await self.ON_CONNECTION_START()

                    # Messages will be sent and received parallely
                    # => both won't block each other
                    await asyncio.gather(self.on_open(websocket), self.receive_message(websocket))

            except Exception as e:
                # Getting the place of error(line of error) 
                # and appending it to the error message

                await self.on_error(e)

        # Creaing a task that wraps the courountine
        self._connection  = asyncio.get_event_loop().create_task(websocket_connect())
        
        # Running the task in the background
        try:
            await self._connection 
        # Avoids that the user notices that the task was cancelled! aka. Silent Error
        except asyncio.CancelledError:
            logger.debug("Connection was cancelled!")
            return 
        except Exception as e:
            logger.critical(e)
            raise sys.exc_info()[0](e)
            

    # Passing values to the Websocket for more information while executing
    async def websocket_init(self, websocket) -> websockets.client.WebSocketClientProtocol:
        """
        
        Initialization Function for the Websocket. Not supposed to be called by user!
        
        """        
        
        websocket.url = self._WEBSOCKET_URL
        websocket.heartbeat = self._HEARTBEAT

        self._websocket = websocket

        return self.websocket


    # Loop for receiving messages from Hiven
    async def receive_message(self, websocket) -> None:
        """
        
        Handler for Receiving Messages. Not supposed to be called by the user! 
        
        """      
        while True:
            response = await websocket.recv()
            if response != None:
                logger.debug(f"Response received: {response}")
                await self.on_response(websocket, response)


    # Opens the event loop
    async def on_open(self, websocket) -> None:
        """
        
        Handler for Opening the Websocket. Not supposed to be called by the user! 
        
        """    
        try:
            async def start_connection():
                logger.info("Connection to Hiven established")
                await self.ON_CONNECTION_START()
                
                while True:
                    # Sleeping the wanted time (Pause for the Heartbeat)
                    await asyncio.sleep(self._HEARTBEAT / 1000)

                    # Lifesignal
                    await websocket.send(json.dumps({"op": 3}))
                    logger.debug("Lifesignal")

                    # If the connection is closing the loop will break
                    if self._connection_status == "closing" or self._connection_status == "closed":
                        logger.info("Connection to Remote () closed!")
                        break

                return 

            self._connection_status = "open"

            connection = asyncio.create_task(start_connection())
            await connection

        except Exception as e:
            logger.critical(f"An error occured while trying to connect to Hiven.")
            raise errs.ConnectionError(f"An error occured while trying to connect to Hiven.\n{e}")


    # Error Handler for exceptions while running the websocket connection
    async def on_error(self, error) -> None:
        """
        
        Handler for Errors in the Websocket. Not supposed to be called by the user! 
        
        """    
        try: line_of_error = sys.exc_info()[-1].tb_lineno
        except Exception as e: line_of_error = "Unknown"
        
        logger.exception(str(error).capitalize())
        raise sys.exc_info()[0](f"In Line {line_of_error}: " + str(error).capitalize())


    # Event Triggers
    async def on_response(self, websocket, ctx_data) -> None:
        """
        
        Handler for the Websocket Events and the message data. Not supposed to be called by the user! 
        
        """    
        try:
            response_data = json.loads(ctx_data)
            
            
            logger.debug(f"Received Event {response_data['e']}")

            if response_data['e'] == "INIT_STATE":
                self.update_client_data(response_data['d'])
                await self.INIT_STATE(time.time())
                self._initalized = True

            elif response_data['e'] == "HOUSE_JOIN":
                
                if not hasattr(self, '_HOUSES') and not hasattr(self, '_USERS'):
                    raise errs.FaultyInitialization("The client attributes _USERS and _HOUSES do not exist! The class might be initialized faulty!")

                house = types.House(response_data['d'])
                await self.HOUSE_JOIN(house)

                for usr in response_data['d']['members']:
                    if not utils.get(self._USERS, id=usr['id'] if hasattr(usr, 'id') else usr['user']['id']):
                        # Appending to the client users list
                        self._USERS.append(types.User(usr))    
                         
                        # Appending to the house users list
                        usr = types.Member(usr)    
                        house._members.append(usr)
                        
                        if usr.joined_at != None:
                           print(types.User(usr).joined_at.year) 
                
                # Appending to the client houses list
                self._HOUSES.append(house)

            elif response_data['e'] == "HOUSE_EXIT":
                ctx = types.Context(response_data['d'])
                await self.HOUSE_EXIT(ctx)

            elif response_data['e'] == "HOUSE_DOWN":
                logger.info(f"Downtime of {response_data['d']['name']} reported!")
                house = None #ToDo
                await self.HOUSE_DOWN(house)

            elif response_data['e'] == "HOUSE_MEMBER_ENTER":
                ctx = types.Context(response_data['d'])
                member = types.Member(response_data['d'])
                await self.HOUSE_MEMBER_ENTER(ctx, member)

            elif response_data['e'] == "HOUSE_MEMBER_EXIT":
                ctx = types.Context(response_data['d'])
                member = types.Member(response_data['d'])
                
                await self.HOUSE_MEMBER_EXIT(ctx, member)

            elif response_data['e'] == "PRESENCE_UPDATE":
                precence = types.Precence(response_data['d'])
                member = types.Member(response_data['d'])
                await self.PRESENCE_UPDATE(precence, member)

            elif response_data['e'] == "MESSAGE_CREATE":
                message = types.Message(response_data['d'])
                await self.MESSAGE_CREATE(message)

            elif response_data['e'] == "MESSAGE_DELETE":
                message = types.Message(response_data['d'])
                await self.MESSAGE_DELETE(message)

            elif response_data['e'] == "MESSAGE_UPDATE":
                message = types.Message(response_data['d'])
                await self.MESSAGE_UPDATE(message)

            elif response_data['e'] == "TYPING_START":
                member = types.Typing(response_data['d'])
                await self.TYPING_START(member)

            elif response_data['e'] == "TYPING_END":
                member = types.Typing(response_data['d'])
                await self.TYPING_END(member)
            
            else:
                logger.debug(f"Unknown Event {response_data['e']} without Handler")
            
        except Exception as e:
            raise sys.exc_info()[0](e)
        
        return

    # Stops the websocket connection
    async def stop_event_loop(self) -> None:
        """
        
        Kills the event loop and the running tasks! 
        
        Will likely throw `RuntimeError` if the Client was started in a courountine or if future courountines are going to get executed!
        
        """
        
        try:
            logger.info(f"Connection to the Hiven Websocket closed!")
            self._connection_status = "closing"
            
            if not self._connection.cancelled():
                self._connection.cancel()
            
            await asyncio.get_event_loop().shutdown_asyncgens()
            asyncio.get_event_loop().stop()
            asyncio.get_event_loop().close()
            
            self._connection_status = "closed"

        except Exception as e:
            logger.critical(f"Error while trying to close the connection{e}")
            raise sys.exc_info()[0](e)
        
        return

    async def close(self) -> None:
        """
        
        Stops the active asyncio task that represents the connection.
        
        """
        try:
            logger.info(f"Connection to the Hiven Websocket closed!")
            self._connection_status = "closing"
            
            if not self._connection.cancelled():
                self._connection.cancel()
                
            self._connection_status = "closed"
        except Exception as e:
            logger.critical(f"An error occured while trying to close the connection to Hiven: {e}")
            raise sys.exc_info()[0](e)
