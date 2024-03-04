from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Peer(_message.Message):
    __slots__ = ("url", "ip_address", "port")
    URL_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    url: str
    ip_address: str
    port: int
    def __init__(self, url: _Optional[str] = ..., ip_address: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class Credentials(_message.Message):
    __slots__ = ("peer", "username", "password")
    PEER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    peer: Peer
    username: str
    password: str
    def __init__(self, peer: _Optional[_Union[Peer, _Mapping]] = ..., username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("message", "status")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    def __init__(self, message: _Optional[str] = ..., status: _Optional[int] = ...) -> None: ...

class Call(_message.Message):
    __slots__ = ("flag",)
    FLAG_FIELD_NUMBER: _ClassVar[int]
    flag: bool
    def __init__(self, flag: bool = ...) -> None: ...

class File(_message.Message):
    __slots__ = ("title", "artist", "album", "duration", "size_MB")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SIZE_MB_FIELD_NUMBER: _ClassVar[int]
    title: str
    artist: str
    album: str
    duration: str
    size_MB: float
    def __init__(self, title: _Optional[str] = ..., artist: _Optional[str] = ..., album: _Optional[str] = ..., duration: _Optional[str] = ..., size_MB: _Optional[float] = ...) -> None: ...

class Dir(_message.Message):
    __slots__ = ("peer", "files")
    PEER_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    peer: Peer
    files: _containers.RepeatedCompositeFieldContainer[File]
    def __init__(self, peer: _Optional[_Union[Peer, _Mapping]] = ..., files: _Optional[_Iterable[_Union[File, _Mapping]]] = ...) -> None: ...
