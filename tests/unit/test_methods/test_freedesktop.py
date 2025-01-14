"""This module tests the Freedesktop.org specific methods. 

These tests do *not* use IO / real or fake Dbus calls. Instead, a special dbus
adapter is used which simply asserts the Call objects and returns what we
would expect from a dbus service."""

import re

import pytest

from wakepy.core.dbus import BusType, DbusAdapter, DbusAddress, DbusMethod
from wakepy.methods.freedesktop import FreedesktopScreenSaverInhibit

screen_saver = DbusAddress(
    bus=BusType.SESSION,
    service="org.freedesktop.ScreenSaver",
    path="/org/freedesktop/ScreenSaver",
    interface="org.freedesktop.ScreenSaver",
)


fake_cookie = 75848243423


def test_screensaver_enter_mode():
    # Arrange
    method_inhibit = DbusMethod(
        name="Inhibit",
        signature="ss",
        params=("application_name", "reason_for_inhibit"),
        output_signature="u",
        output_params=("cookie",),
    ).of(screen_saver)

    class TestAdapter(DbusAdapter):
        def process(self, call):
            assert call.method == method_inhibit
            assert call.get_kwargs() == {
                "application_name": "wakepy",
                "reason_for_inhibit": "wakelock active",
            }

            return (fake_cookie,)

    method = FreedesktopScreenSaverInhibit(dbus_adapter=TestAdapter())
    assert method.inhibit_cookie is None

    # Act
    enter_retval = method.enter_mode()

    # Assert
    assert enter_retval is None
    # Entering mode sets a inhibit_cookie to value returned by the DbusAdapter
    assert method.inhibit_cookie == fake_cookie


def test_screensaver_exit_mode():
    # Arrange
    method_uninhibit = DbusMethod(
        name="UnInhibit",
        signature="u",
        params=("cookie",),
    ).of(screen_saver)

    class TestAdapter(DbusAdapter):
        def process(self, call):
            assert call.method == method_uninhibit
            assert call.get_kwargs() == {"cookie": fake_cookie}

    method = FreedesktopScreenSaverInhibit(dbus_adapter=TestAdapter())
    method.inhibit_cookie = fake_cookie

    # Act
    exit_retval = method.exit_mode()

    # Assert
    assert exit_retval is None
    # exiting mode unsets the inhibit_cookie
    assert method.inhibit_cookie is None


def test_screensaver_exit_before_enter():
    method = FreedesktopScreenSaverInhibit(dbus_adapter=DbusAdapter())
    assert method.inhibit_cookie is None
    assert method.exit_mode() is None


def test_with_dbus_adapter_which_returns_none():
    class BadAdapterReturnNone(DbusAdapter):
        def process(self, _):
            return None

    method = FreedesktopScreenSaverInhibit(dbus_adapter=BadAdapterReturnNone())

    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "Could not get inhibit cookie from org.freedesktop.ScreenSaver"
        ),
    ):
        assert method.enter_mode() is False
