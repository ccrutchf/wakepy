from __future__ import annotations

import typing
from typing import List, NamedTuple, Tuple, Type, Union

from . import BusType
from .calls import DbusMethodCall

if typing.TYPE_CHECKING:
    from typing import Any, Optional


DbusAdapterSeq = typing.Union[List["DbusAdapter"], Tuple["DbusAdapter", ...]]
DbusAdapterTypeSeq = typing.Union[
    List[Type["DbusAdapter"]], Tuple[Type["DbusAdapter"], ...]
]


class DbusAddress(NamedTuple):
    """The dbus object and interface specification. This uniquelly defines the
    interface to connect with."""

    service: str
    """The well known bus name of the dbus service to connect with.
    This is like a domain address, but on D-Bus. There might be multiple
    objects (specified by their paths) with multiple interfaces on single
    service.

    Example: "org.spam.Manager"
    """

    path: str
    """The path of the object to connect with. One object, defined by the
    bus, service and path, might have multiple interfaces.

    Example: "/org/spam/Manager"
    """

    interface: str
    """The name of the interface on the object. Interface defines which methods
    (or: members) are available on the object. One interface can, and usually
    does, define multiple methods.

    Example: "org.spam.Manager"
    """

    bus: Optional[Union[str, BusType]] = BusType.SESSION
    """The type of message bus used. Should be "SESSION" or "SYSTEM".
    Each running dbus-daemon process provides a new message bus.
    If omitted, session bus is assumed.   
    """


class DbusMethod(NamedTuple):
    """The dbus method specification. Uniquely defines a D-Bus method.

    It is said to be completely defined, when it is tied to a  DBusAddress;
    when it has `bus`, `service`, `path` and `interface`. Otherwise, it is
    partially defined. Tying is done with the .of() method.
    """

    name: str
    """name of the method, without the interface part. For example if creating
    method for  "org.spam.Manager.SomeMethod", the method name is "SomeMethod". 
    """

    signature: str | None
    """The signature for the method input parameters.

    The types are: (Conventional name, ASCII type-code, meaning)
    
    BYTE	y (121)	Unsigned 8-bit integer
    BOOLEAN	b (98)	Boolean value: 0 is false, 1 is true
    INT16	n (110)	Signed 16-bit integer
    UINT16	q (113)	Unsigned 16-bit integer
    INT32	i (105)	Signed 32-bit integer
    UINT32	u (117)	Unsigned 32-bit integer
    INT64	x (120)	Signed 64-bit integer
    UINT64	t (116)	Unsigned 64-bit integer
    DOUBLE	d (100)	IEEE 754 double-precision floating point
    UNIX_FD	h (104)	Unsigned 32-bit integer representing an index into an
                    out-of-band array of file descriptors, transferred via some
                    platform-specific mechanism
    STRING  s (115) String
    
    Ref: https://dbus.freedesktop.org/doc/dbus-specification.html
    """
    params: Optional[tuple[str, ...]] = None
    """The names of the input arguments defined by the `signature`.
    This is optional, but highly recommended, as it serves as documentation
    and removes the need for writing comments for the signature.
    """

    output_signature: str | None = None
    """The signature for the method output / return values. See the docs for
    signature. 
    """

    output_params: Optional[tuple[str, ...]] = None
    """The names of the output parameters defined by the `output_signature`.
    This is optional, but highly recommended, as it serves as documentation
    and removes the need for writing comments for the signature.
    """

    # The following attributes are same as with DbusAddress
    service: Optional[str] = None
    """The well known bus name of the dbus service to connect with.
    This is like a domain address, but on D-Bus. There might be multiple
    objects (specified by their paths) with multiple interfaces on single
    service.

    Example: "org.spam.Manager"
    """

    path: Optional[str] = None
    """The path of the object to connect with. One object, defined by the
    bus, service and path, might have multiple interfaces.

    Example: "org/spam/Manager"
    """

    interface: Optional[str] = None
    """The name of the interface on the object. Interface defines which methods
    (or: members) are available on the object. One interface can, and usually
    does, define multiple methods.

    Example: "org.spam.Manager"
    """

    bus: Optional[Union[str, BusType]] = BusType.SESSION
    """The type of message bus used. Should be "SESSION" or "SYSTEM".
    Each running dbus-daemon process provides a new message bus.
    If omitted, session bus is assumed.   
    """

    def of(
        self,
        addr: DbusAddress,
    ):
        """Ties a DBusAddress to a DBusMethod, forming a completely defined
        DBusMethod. Returns a new DBusMethod object.
        """
        return type(self)(
            name=self.name,
            signature=self.signature,
            params=self.params,
            output_signature=self.output_signature,
            output_params=self.output_params,
            service=addr.service,
            path=addr.path,
            interface=addr.interface,
            bus=addr.bus,
        )

    def completely_defined(self) -> bool:
        return all(
            x is not None for x in (self.service, self.path, self.interface, self.bus)
        )

    def to_call(
        self, args: dict[str, Any] | Tuple[Any, ...] | List[Any]
    ) -> DbusMethodCall:
        return DbusMethodCall(self, args)


class DbusAdapter:
    """Defines the DbusAdapter interface. This is to be subclassed, and each
    subclass is usually an implementation for a DbusAdapter using single
    python (dbus-)library.

    When subclassing, implement the .process(call) method. The call
    (DbusMethodCall) tells which bus to use (session/system/custom addr), and
    therefore the connection must be created within the .process() call (this
    can of course be cached).

    The __init__() should not take any arguments, and it may raise any subtype
    of Exception, which simply means that the DbusAdapter may not be used. The
    Exception will be omitted if using the high-level API of wakepy.
    """

    def process(self, call: DbusMethodCall):
        ...
