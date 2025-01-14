(wakepy-methods)=
# List of Wakepy Methods


**What are wakepy Methods?**
Methods are different ways of entering/keeping in a Mode. A Method may support one or more platforms, and may have one or more requirements for software it should be able to talk to or execute. For example, on Linux. using the Inhibit method of the [org.gnome.SessionManager](#keep-running-org-gnome-sessionmanager) D-Bus service is one way of entering  the [`keep.running`](#keep-running-section) mode, and it required D-Bus and (a certain version of) GNOME. The following methods exist:


```{contents}
:local: True
:depth: 2
:class: this-will-duplicate-information-and-it-is-still-useful-here
```

(keep-running-section)=
## keep.running

(keep-running-org-gnome-sessionmanager)=
### org.gnome.SessionManager
- **Name**: `org.gnome.SessionManager`
- **Introduced in**: wakepy 0.8.0
- **How it works**: Uses the [Inhibit](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.Inhibit) method of [org.gnome.SessionManager](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager) D-Bus service with flag 4 ("Inhibit suspending the session or computer") when activating and saves the returned cookie on the Method instance. Uses the [Uninhibit](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.Uninhibit) method of the org.gnome.SessionManager with the cookie when deactivating.  
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed.
- **How to check it?**:  You may check the list of inhibitors using the [GetInhibitors](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.GetInhibitors) method, which gives you list of object paths like `["/org/gnome/SessionManager/Inhibitor20"]`. Then you can use the [GetAppId](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.Inhibitor.GetAppId), [GetFlags](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.Inhibitor.GetFlags) and [GetReason](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.Inhibitor.GetReason) methods on the [org.gnome.SessionManager.Inhibitor](https://lira.no-ip.org:8443/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.Inhibitor) interface of the listed objects on the org.gnome.SessionManager service to translate that into something meaningful. A good tool for this is [D-Spy](https://apps.gnome.org/Dspy/). Alternatively, you could monitor your inhibit call with [`dbus-monitor`](https://dbus.freedesktop.org/doc/dbus-monitor.1.html).
- **Requirements**: D-Bus, GNOME Desktop Environment with gnome-session running. The exact version of required GNOME is unknown, but this should work from GNOME 2.24 ([2008-09-23](https://gitlab.gnome.org/GNOME/gnome-session/-/tags/GNOME_SESSION_2_24_0)) onwards. See [version history of org.gnome.SessionManager.xml](https://gitlab.gnome.org/GNOME/gnome-session/-/commits/main/gnome-session/org.gnome.SessionManager.xml). At least [this](https://fedoraproject.org/wiki/Desktop/Whiteboards/InhibitApis) and [this](https://bugzilla.redhat.com/show_bug.cgi?id=529287#c3) mention GNOME 2.24.
- **Tested on**:  Ubuntu 22.04.3 LTS with GNOME 42.9 ([PR #138](https://github.com/fohrloop/wakepy/pull/138) by [fohrloop](https://github.com/fohrloop/)).

(keep-running-windows-stes)=
### SetThreadExecutionState

````{admonition} Windows will not lock the screen automatically if Screen Saver settings do not require it
:class: warning

Since this method prevents sleep, screen can be only locked automatically if a screen saver is enabled and it set to ask for password. See [this](#checking-if-windows-will-lock-screen-automatically) for details.


````

- **Name**: `SetThreadExecutionState`
- **Introduced in**: wakepy 0.1.0
- **How it works**: It calls the [SetThreadExecutionState](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate) function from the Kernel32.dll with ES_CONTINUOUS and ES_SYSTEM_REQUIRED flags when activating, and with ES_CONTINUOUS when deactivating. Note that currently it is not possible to use two wakepy modes using SetThreadExecutionState at the same time in the same thread! (See: [Issue 167](https://github.com/fohrloop/wakepy/issues/167))
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed.
- **How to check it?**: Run `powercfg /requests` in an elevated cmd or Powershell.
- **Requirements**: Windows XP or higher (client), Windows Server 2003 or higher (server), as mentioned [here](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate).
- **Tested on**:  Windows 10 Pro version 22H2 build 19045.332 with and without Screen Saver + ScreenSaverIsSecure set in settings, Windows 10 Enterprise version 22H2 build 19045.3803 with Group Policies enforcing ScreenSaverIsSecure ([Issue #169](https://github.com/fohrloop/wakepy/issues/169) by [fohrloop](https://github.com/fohrloop/)).


 (checking-if-windows-will-lock-screen-automatically)=
````{admonition} How to check if Windows will lock the screen automatically when using SetThreadExecutionState
:class: info

There are two ways how a Windows system might automatically set a screen lock
1. When resuming from sleep, if "Require sign-in when PC wakes up from sleep" -setting is set.
2. When Screen Saver idle timeout is reached *and it has set to have password protection in the Lock Screen Setting or that is enforced by a Group Policy*.

if you want to check if your system will sleep automatically when using this method, you may either check the  `ScreenSaverIsSecure`, `ScreenSaveActive` and `ScreenSaveTimeout` from  "HKCU:\Control Panel\Desktop" and "HKCU:\Software\Policies\Microsoft\Windows\Control Panel\Desktop", or use the following python snippet: 

```python
import ctypes

SPI_GETSCREENSAVESECURE = 0x0076
SPI_GETSCREENSAVEACTIVE = 0x0010
SPI_GETSCREENSAVETIMEOUT = 0x000E

retval = ctypes.c_long()
pvparam = ctypes.byref(retval)

result = ctypes.windll.user32.SystemParametersInfoW(SPI_GETSCREENSAVEACTIVE, 0, pvparam, 0)
print('SPI_GETSCREENSAVEACTIVE', retval.value)

result = ctypes.windll.user32.SystemParametersInfoW(SPI_GETSCREENSAVESECURE, 0, pvparam, 0)
print('SPI_GETSCREENSAVESECURE', retval.value)

result = ctypes.windll.user32.SystemParametersInfoW(SPI_GETSCREENSAVETIMEOUT, 0, pvparam, 0)
print('SPI_GETSCREENSAVETIMEOUT', retval.value)
```


````

(keep-running-macos-caffeinate)=
### caffeinate

- **Name**: `caffeinate`
- **Introduced in**: wakepy 0.3.0
- **How it works**: It calls the `caffeinate` command. See docs at [ss64.com](https://ss64.com/mac/caffeinate.html) or at archives from [developer.apple.com](https://web.archive.org/web/20140604153141/https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/caffeinate.8.html)
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed. 
- **How to check it?**: You should be able to see a process with a command `/bin/bash caffeinate` or similar associated with it using a task manager.
- **Requirements**: Mac OS X 10.8 Mountain Lion (July 2012) or newer.


## keep.presenting


### org.gnome.SessionManager

- **Name**: `org.gnome.SessionManager`
- **Introduced in**: wakepy 0.8.0
- **How it works**: Exactly the same as the [keep.running](#keep-running-org-gnome-sessionmanager) using org.gnome.SessionManager, but using the flag 8 ("Inhibit the session being marked as idle").
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed.
- **How to check it?**: Similarly as checking [keep.running](#keep-running-org-gnome-sessionmanager) using org.gnome.SessionManager.
- **Requirements**: Same as [keep.running](#keep-running-org-gnome-sessionmanager) using org.gnome.SessionManager.
- **Tested on**:  Ubuntu 22.04.3 LTS with GNOME 42.9 ([PR #138](https://github.com/fohrloop/wakepy/pull/138) by [fohrloop](https://github.com/fohrloop/)).

(keep-presenting-org-freedesktop-screensaver)=
### org.freedesktop.ScreenSaver
- **Name**: `org.freedesktop.ScreenSaver`
- **Introduced in**: wakepy 0.6.0
- **How it works**: Uses the Inhibit method of [org.freedesktop.ScreenSaver](https://people.freedesktop.org/~hadess/idle-inhibition-spec/re01.html) D-Bus service when activating and saves the returned cookie on the Method instance. Uses the org.freedesktop.ScreenSaver.UnInhibit method with the cookie when deactivating. The org.freedesktop.ScreenSaver can only be used to prevent idle; that is why there is no "keep.running" mode counterpart.  
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed.
- **How to check it?**:  The org.freedesktop.ScreenSaver does not expose a method for listing the inhibitors, but you could monitor your inhibit call with [`dbus-monitor`](https://dbus.freedesktop.org/doc/dbus-monitor.1.html).
- **Requirements**: D-Bus, and a [freedesktop.org compliant desktop environment](https://www.freedesktop.org/wiki/Desktops/), which should implement the org.freedesktop.ScreenSaver.Inhibit method. 
- **Tested on**:  Ubuntu 22.04 with GNOME 42.9 ([PR #171](https://github.com/fohrloop/wakepy/pull/171) by [fohrloop](https://github.com/fohrloop/)).

(keep-presenting-windows-stes)=
### SetThreadExecutionState



- **Name**: `SetThreadExecutionState`
- **Introduced in**: wakepy 0.1.0
- **How it works**: Exactly the same as the [keep.running](keep-running-windows-stes), but using ES_CONTINUOUS, ES_SYSTEM_REQUIRED *and* ES_DISPLAY_REQUIRED flags when activating.
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed.
- **How to check it?**: Like the [keep.running](keep-running-windows-stes)
- **Requirements**: Same as for the [keep.running](keep-running-windows-stes) using SetThreadExecutionState.
- **Tested on**:  Windows 10 Pro version 22H2 build 19045.332 with and without Screen Saver + ScreenSaverIsSecure set in settings, Windows 10 Enterprise version 22H2 build 19045.3803 with Group Policies enforcing ScreenSaverIsSecure ([Issue #169](https://github.com/fohrloop/wakepy/issues/169) by [fohrloop](https://github.com/fohrloop/)).





(keep-presenting-macos-caffeinate)=
### caffeinate

- **Name**: `caffeinate`
- **Introduced in**: wakepy 0.3.0
- **How it works**: It calls the `caffeinate` command with `-d` flag ("Create an assertion to prevent the display from sleeping."). See docs at [ss64.com](https://ss64.com/mac/caffeinate.html) or at archives from [developer.apple.com](https://web.archive.org/web/20140604153141/https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/caffeinate.8.html)
- **Multiprocess safe?**: Yes
- **What if the process holding the lock dies?**: The lock is automatically removed. 
- **How to check it?**: You should be able to see a process with a command `/bin/bash caffeinate -d` or similar associated with it using a task manager.
- **Requirements**: Mac OS X 10.8 Mountain Lion (July 2012) or newer.

