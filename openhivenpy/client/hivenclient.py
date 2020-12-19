import asyncio
from openhivenpy.gateway.connection import ExecutionLoop
from openhivenpy.gateway.ws import Websocket
import sys
import nest_asyncio
import logging
from time import time
from typing import Optional, Union
from datetime import datetime

from openhivenpy.gateway import Connection, API, HTTP
from openhivenpy.events import EventHandler
import openhivenpy.exceptions as errs
import openhivenpy.utils as utils
import openhivenpy.types as types

__all__ = 'HivenClient'

logger = logging.getLogger(__name__)


def _check_dependencies() -> None:
    pkgs = ['asyncio', 'typing', 'aiohttp']
    for pkg in pkgs:
        if pkg not in sys.modules:
            logger.critical(f"Module {pkg} not found in locally installed modules!")
            raise ImportError(f"Module {pkg} not found in locally installed modules!", name=pkg)


class HivenClient(EventHandler, API):
    """`openhivenpy.client.HivenClient` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Main Class for connecting to Hiven and interacting with the API.
    
    Inherits from EventHandler and API
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven.
                    Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    restart: `bool` - If set to `True` the process will restart if an error occurred while running the websocket.
                    If the restart failed again the program will stop. Defaults to `False`
    
    client_type: `str` - Automatically set if UserClient or BotClient is used.
                        Raises `HivenException.InvalidClientType` if set incorrectly. Defaults to `BotClient`
    
    event_handler: `openhivenpy.events.EventHandler` - Handler for the events. Can be modified and customized if wanted.
                                                        Creates a new one on Default
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
   
    log_ws_output: `bool` - Will additionally to normal debug information also log the ws responses
    
    ping_timeout: `int` - Seconds after the websocket will timeout after no successful pong response.
                        More information on the websockets documentation. Defaults to `100`
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the handshake
                            didn't complete successfully. Defaults to `20`
    
    ping_interval: `int` - Interval for sending pings to the server. Defaults to `None` because else the websocket
                        would timeout because the Hiven Websocket does not give a response!
    
    event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions.
                                                        Creates a new one on default
    
    """
<<<<<<< HEAD
    def __init__(
                self,
                token: str,
                *,
                event_handler: EventHandler = None,
                client_type: str = None,
                event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
                **kwargs):

        # Calling super to make the client it's own event_handler
        super().__init__(self)
=======

    def __init__(self, token: str, *, client_type: str = None, event_handler: EventHandler = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(), **kwargs):

        super().__init__()
>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
        if client_type == "user" or client_type == "HivenClient.UserClient":
            self._CLIENT_TYPE = "user"
            self._bot = False

        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self._CLIENT_TYPE = "bot"
            self._bot = True

        elif client_type is None:
<<<<<<< HEAD
            logger.warning("[CLIENT] >> Client type is None. Defaulting to BotClient.")
=======
            logger.warning(
                "[CLIENT] >> Client type is None. Defaulting to BotClient. This might be caused by using the "
                "HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!")
>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
            self._CLIENT_TYPE = "bot"
            self._bot = True

        else:
            logger.error(f"[CLIENT] >> Expected 'user' or 'bot', got '{client_type}'")
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'")

        if token is None or token == "":
            logger.critical(f"[CLIENT] >> Empty Token was passed!")
            raise errs.InvalidToken

        elif len(token) != 128 and len(token) != 132:  # Bot TOKEN
            logger.critical(f"[CLIENT] >> Invalid Token was passed!")
            raise errs.InvalidToken

        _check_dependencies()

        self._TOKEN = token
        self.loop = event_loop
<<<<<<< HEAD

        if not event_handler:
            self.event_handler = self
        else:
            self.event_handler = event_handler
=======
        # User Customizable Event Handler
        self.event_handler = EventHandler(self) if event_handler is None else event_handler
>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90

        # Websocket and client data are being handled over the Connection Class
        self.connection = Connection(event_handler=self.event_handler,
                                     token=token,
                                     event_loop=self.loop,
                                     **kwargs)
<<<<<<< HEAD
=======

        # Not sure if that's a good solution to the issue but I will do this
>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
        nest_asyncio.apply(loop=self.loop)

    @property
    def token(self) -> str:
        return self._TOKEN

    @property
<<<<<<< HEAD
    def http(self) -> HTTP:
        return self.connection.http
        
=======
    def http_client(self) -> HTTPClient:
        return self.connection.http_client

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
    async def connect(self) -> None:
        """`openhivenpy.client.HivenClient.connect()`
        
        Async function for establishing a connection to Hiven
        
        """
        try:
            self.loop.run_until_complete(self.connection.connect())
        except RuntimeError as e:
            logger.exception(e)
            raise errs.HivenConnectionError(f"Failed to start client session and websocket! Cause of Error: {e}")
        finally:
            return

    def run(self) -> None:
        """`openhivenpy.client.HivenClient.run()`
        
        Standard function for establishing a connection to Hiven
        
        """
        try:
            self.loop.run_until_complete(self.connection.connect())
        except RuntimeError as e:
            logger.exception(e)
            raise errs.HivenConnectionError(
                f"Failed to start session and establish connection to Hiven! Cause of Error: {e}")
        finally:
            return

    async def destroy(self):
        """`openhivenpy.HivenClient.destroy()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw a RuntimeError if the client was started in a coroutine or if future coroutines
        are going to get executed!
        
        """
        try:
            if self.connection.closed:
                await self.connection.destroy()
                return True
            else:
                logger.error(
                    "[CLIENT] << An attempt to close the connection to Hiven failed due to no current active "
                    "Connection!")
                return False
        except Exception as e:
            logger.error(
                f"[CLIENT] << Failed to close client session and websocket to Hiven! Cause of Error: "
                f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(
                f"Failed to close client session and websocket to Hiven! Cause of Error: "
                f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")

    async def close(self) -> bool:
        """`openhivenpy.HivenClient.close()`
        
        Stops the active asyncio task that represents the connection.
        
        Returns `True` if successful
        
        """
        try:
            if self.connection.closed:
                await self.connection.close()
                return True
            else:
                logger.error("[CLIENT] << An attempt to close the connection to Hiven failed "
                             "due to no current active Connection!")
                return False
        except Exception as e:
            logger.error(
                f"[CLIENT] << Failed to close client session and websocket to Hiven! Cause of Error: "
                f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(
                f"Failed to close client session and websocket to Hiven! Cause of Error: "
                f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")

    @property
    def client_type(self) -> str:
        return self._CLIENT_TYPE

    @property
    def ready(self) -> bool:
        return self.connection.ready

    @property
    def initialized(self) -> bool:
        """`openhivenpy.HivenClient.initialized`

        True if Websocket and HTTP are connected and running

        """
        return self.connection.initialized

    # Meta data
    # -----------
    @property
    def amount_houses(self) -> list:
        return  self.connection._amount_houses

    @property
    def houses(self) -> list:
        return self.connection._houses

    @property
    def users(self) -> list:
        return self.connection._users

    @property
    def rooms(self) -> list:
        return self.connection._rooms

    @property
    def private_rooms(self) -> list:
        return self.connection._private_rooms

    @property
    def relationships(self) -> list:
        return self.connection._relationships

    # Client data
    # -----------
    @property
    def username(self) -> str:
        return self.connection.username

    @property
    def name(self) -> str:
        return self.connection.name

    @property
    def id(self) -> int:
        return self.connection.id

    @property
    def icon(self) -> str:
        return f"https://media.hiven.io/v1/users/{self.id}/icons/{self.connection.icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self.id}/headers/{self.connection.header}"

    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def location(self) -> str:
        return self.connection.location

    @property
    def website(self) -> str:
        return self.connection.website

    @property
    def joined_at(self) -> datetime:
        return self.connection.joined_at

    @property
    def presence(self):
        return self.connection.presence

    # General Connection Properties    
    @property
    def heartbeat(self) -> int:
        return self.connection.heartbeat

    @property
    def connection_status(self) -> str:
        """`openhivenpy.HivenClient.get_connection_status`

        Returns a string with the current connection status.
        
        Can be either 'OPENING', 'OPEN', 'CLOSING' or 'CLOSED'

        """
        return self.connection.connection_status

    @property
    def open(self) -> bool:
        """`openhivenpy.HivenClient.websocket`
        
        Returns `True` if the connection is open
        
        Opposite property to closed
        
        """
        return self.connection.open

    @property
    def closed(self) -> bool:
        """`openhivenpy.HivenClient.closed`

        Returns `True` if the connection is closed
        
        Opposite property to open
        
        """
        return self.connection.closed

    @property
    def ws(self) -> Websocket:
        """`openhivenpy.HivenClient.websocket`
        
        Returns the ReadOnly Websocket with it's configuration
        
<<<<<<< HEAD
        """    
        return self.connection.ws
    
=======
        """
        return self.connection.websocket

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
    @property
    def execution_loop(self) -> ExecutionLoop:
        return self.connection.execution_loop

    @property
    def connection_start(self) -> float:
        """`openhivenpy.HivenClient.connection_start`

        Point of connection start in unix dateformat
        
        """
        return self.connection.connection_start

    @property
    def startup_time(self) -> float:
        return self.connection.startup_time

    @property
    def ping(self) -> Union[float, None]:
        """`openhivenpy.client.HivenClient.ping`
        
        Returns the current ping of the HTTP.
        
        """
        if self.http._ready:
            start_t = time()
            resp = asyncio.run(self.http.raw_request("/users/@me", method="get"))
            if not resp:
                raise errs.HTTPFaultyResponse

            if resp.status == 200:
                return time() - start_t
            else:
                logger.warning("[CLIENT] >> Trying to ping Hiven failed!")
                return None
        else:
            return None
<<<<<<< HEAD
=======

    @property
    def connection_possible(self) -> bool:
        """`openhivenpy.client.HivenClient.connection_possible()`
        
        Checks whether the connection to Hiven is alive and possible!

        Alias for ping() but does not need the client to be connected!
        
        """
        res = requests.get("https://api.hiven.io/")
        if res.status_code == 200:
            return True
        else:
            logger.warning("[CLIENT] >> The attempt to ping Hiven failed!")
            return False
>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90

    async def edit(self, data: str, value: str) -> bool:
        """`openhivenpy.HivenClient.edit()`
        
        Change the signed in user's/bot's data. 
        
        Available options: header, icon, bio, location, website.
        
        Alias for HivenClient.connection.edit()
        
        """
        if self.http._ready:
            return await self.connection.edit(data=data, value=value)
        else:
            logging.error("HTTP Request was attempted without active Connection!")
            raise errs.HivenConnectionError("HTTP Request was attempted without active Connection!")

    async def getRoom(self, room_id: int) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.getRoom()`
        
        Returns a cached Hiven Room Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_room()
        
        """
        return utils.get(self.rooms, id=room_id)

    async def getHouse(self, house_id: int) -> Union[types.House, None]:
        """`openhivenpy.HivenClient.getHouse()`
        
        Returns a cached Hiven Room Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_house()
        
        """
        return utils.get(self.houses, id=house_id)

    async def getUser(self, user_id: int) -> Union[types.User, None]:
        """`openhivenpy.HivenClient.getUser()`
        
        Returns a cached Hiven User Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_user()
    
        """
        return utils.get(self.users, id=user_id)

    async def get_house(self, house_id: int) -> Union[types.House, None]:
        """`openhivenpy.HivenClient.get_house()`
        
        Returns a Hiven House Object based on the passed id.
        
        Returns the House if it exists else returns None
        
        """
        try:
            cached_house = utils.get(self.houses, id=house_id)
            if cached_house is not None:
                return cached_house

                # Not yet possible
                # data = await self.http.request(endpoint=f"/houses/{id}")
                # house = House(data['d'], self.http, self.id)
                # if cached_house:
                #    self.connection._houses.remove(cached_house)
                # self.connection._houses.append(house)
                # return house
            return None
        except Exception as e:
            logger.error(f"[CLIENT] >> Failed to get House based with id {house_id}! Cause of error: {e}")

    async def get_user(self, user_id: int) -> Union[types.User, None]:
        """`openhivenpy.HivenClient.get_user()`
        
        Returns a Hiven User Object based on the passed id.
        
        Returns the House if it exists else returns None
        
        """
        try:
            cached_user = utils.get(self.users, id=user_id)
            if cached_user is not None:
                data = await self.http.request(endpoint=f"/users/{id}")
                user = types.User(data['d'], self.http)
                if cached_user:
                    self.connection._houses.remove(cached_user)
                self.connection._houses.append(user)
                return user
            return None
        except Exception as e:
            logger.error(f"[CLIENT] >> Failed to get User based with id {user_id}! Cause of error: {e}")

    async def get_room(self, room_id: int) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.get_room()`
        
        Returns a Hiven Room Object based on the passed house id and room id.
        
        Returns the Room if it exists else returns None
        
        """
        try:
            cached_room = utils.get(self.rooms, id=room_id)
            if cached_room is not None:
                data = await self.http.request(endpoint=f"/rooms/{room_id}")
                house = cached_room.house
                room = types.Room(data['d'], self.http, house)
                if cached_room:
                    self.connection._houses.remove(cached_room)
                self.connection._houses.append(room)

                return room
            return None
        except Exception as e:
            logger.error(f"[CLIENT] >> Failed to get Room based with id {room_id}! Cause of error: {e}")

    async def get_private_room(self, room_id: float) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.get_private_room()`
        
        Returns a Hiven `PrivateRoom` or `GroupChatRoom` Object based on the passed house id and room id.
        
        Returns the Room if it exists else returns None
        
        """
        try:
            cached_private_room = utils.get(self.private_rooms, id=room_id)
            if cached_private_room is not None:
                data = await self.http.request(endpoint=f"/rooms/{room_id}")
                if data is not None:
                    room = types.Room(data['d'], self.http, None)
                    return room
                else:
                    return cached_private_room
            return None

        except Exception as e:
            logger.error(f"[CLIENT] >> Failed to get Room based with id {room_id}! Cause of error: {e}")

    async def create_house(self, name: str) -> types.LazyHouse:
        """`openhivenpy.HivenClient.create_house()`
        
        Creates a new house on Hiven if the limit is not yet reached
        
        Returns a low-level form of the House object!

        Note! The returned house does not have all the necessary data and only the basic data!
        To get the regular house use `utils.get(client.houses, id=house_id)`
        
        """
        try:
<<<<<<< HEAD
            resp = await self.http.post(
                                                endpoint="/houses",
                                                json={'name': name})
=======
            resp = await self.http_client.post(
                endpoint="/houses",
                json={'name': name})
>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
            if resp is None or resp.status >= 300:
                raise errs.HTTPRequestError("Internal request error!")

            data = await resp.json()
            house = types.LazyHouse(data.get('data'), self.http)
            await asyncio.sleep(0.2)
            return house

        except Exception as e:
            logger.error(f"Failed to create House! Cause of error: {e}")

    async def delete_house(self, house_id: int) -> Union[int, None]:
        """`openhivenpy.HivenClient.delete_house()`
        
        Deletes a house based on passed id on Hiven
        
        Returns the id of the House if successful
        
        Parameter
        ~~~~~~~~~
        
        house_id: `int` - Id of the house
        
        """
        try:
            cached_house = utils.get(self.houses, id=int(house_id))
            if cached_house:
<<<<<<< HEAD
                resp = await self.http.delete(endpoint=f"/houses/{house_id}")
                
=======
                resp = await self.http_client.delete(endpoint=f"/houses/{house_id}")

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
                if resp.status < 300:
                    return self.id
                else:
                    return None
            else:
                logger.error(f"The house with id {house_id} does not exist in the client cache!")
                return None

        except Exception as e:
            logger.error(f"Failed to delete House! Cause of error: {e}")

    async def fetch_invite(self, invite_code: str) -> Union[types.Invite, None]:
        """`openhivenpy.HivenClient.get_invite()`
        
        Fetches an invite from Hiven
        
        Returns an `Invite` Object
        
        """
        try:
<<<<<<< HEAD
            data = await self.http.request(endpoint=f"/invites/{invite_code}")
            
            return types.Invite(data.get('data'), self.http)
         
=======
            data = await self.http_client.request(endpoint=f"/invites/{invite_code}")

            return types.Invite(data.get('data'), self.http_client)

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
        except Exception as e:
            logger.error(f"Failed to fetch the invite with invite_code {invite_code}! Cause of error: {e}")

    async def get_feed(self) -> Union[types.Feed, None]:
        """`openhivenpy.HivenClient.get_feed()`
        
        Get the current users feed
        
        Returns an `Feed` Object
        
        """
        try:
            data = await self.http.request(endpoint=f"/streams/@me/feed")
            if data is not None:
                return types.Feed(data, self.http)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get the users feed! Cause of error: {e}")

    async def get_mentions(self) -> Union[list, types.Mention]:
        """`openhivenpy.HivenClient.get_mentions()`
        
        Gets all mentions of the client user
        
        Returns a list of `Mention` Objects
        
        """
        try:
<<<<<<< HEAD
            resp = await self.http.request(endpoint=f"/streams/@me/mentions")
            
=======
            resp = await self.http_client.request(endpoint=f"/streams/@me/mentions")

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
            data = resp.get('data')

            mention_list = []
            for msg_data in data:
<<<<<<< HEAD
                author = types.User(msg_data.get('author'), self.http)
                
=======
                author = types.User(msg_data.get('author'), self.http_client)

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
                room = utils.get(self.rooms, id=int(msg_data.get('room_id')))

                message = types.Message(
<<<<<<< HEAD
                                    msg_data, 
                                    self.http,
                                    room.house,
                                    room,
                                    author)
                
=======
                    msg_data,
                    self.http_client,
                    room.house,
                    room,
                    author)

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
                mention_list.append(message)

            return mention_list

        except Exception as e:
            logger.error(f"Failed to get the users mentions! Cause of error: {e}")

    async def change_room_settings(self, room_id=None, **kwargs) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.change_room_settings()`
 
        Changed a room settings if permission are sufficient!
        
        Returns the `Room` object if the room exists in the known rooms
 
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request!
        
        room_id: `int` - Id of the room that should be modified

        room: `openhivenpy.types.Room` - Room object that should be modified
        
        Available Options
        ~~~~~~~~~~~~~~~~~
        
        notification_preference: `int` - Notification preference for the room. 0 = 'all'/1 = 'mentions'/2 = 'none'
        
        """
        try:
            if room_id is None:
                room = kwargs.get('room')
                try:
                    room_id = room.id
                except Exception:
                    room = None
                if room_id is None:
                    logger.debug("Invalid parameter for block_user! Expected user or user_id!")
                    return None
            else:
                json = {}
                for key in kwargs:
                    if key in ['notification_preference', 'name']:
                        json['key'] = kwargs.get(key)
<<<<<<< HEAD
                        
                resp = await self.http.put(
                                                endpoint=f"/users/@me/settings/room_overrides/{room_id}",
                                                json=json)
                
=======

                resp = await self.http_client.put(
                    endpoint=f"/users/@me/settings/room_overrides/{room_id}",
                    json=json)

>>>>>>> 3415c7360778fc89a254beac037917a4da5e4b90
                if resp.status < 300:
                    return utils.get(self.rooms, id=int(room_id))
                else:
                    return None

        except Exception as e:
            logger.error(f"Failed to edit the room with id {room_id}. Cause of Error {e}")
            return None

    async def create_private_room(self, user_id=None, **kwargs) -> Union[types.PrivateRoom, None]:
        """`openhivenpy.UserClient.create_private_room()`
 
        Adds a user to a private chat room where you can send messages.
        
        Called when trying to send a message to a user and not room exists yet
        
        Returns the `User` object if the user exists in the known users
 
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request!
        
        user_id: `int` - Id of the user that should be added to a private room
        
        user: `openhivenpy.types.User` - User object that should be added to a private room
        
        """
        try:
            if user_id is None:
                user = kwargs.get('user')
                try:
                    user_id = user.id
                except Exception:
                    user_id = None
                if user_id is None:
                    logger.debug("Invalid parameter for create_private_room! Expected user or user_id!")
                    return None
            else:
                resp = await self.http.post(endpoint=f"/users/@me/rooms",
                                                   json={'recipient': f"{user_id}"})
                if resp.status < 300:
                    data = await resp.json()
                    private_room = types.PrivateRoom(data.get('data'), self.http)
                    self.connection._private_rooms.append(private_room)
                    return private_room
                else:
                    return None

        except Exception as e:
            logger.error(f"Failed to send a friend request a user with id {user_id}! Cause of Error {e}")
            return None
