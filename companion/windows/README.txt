TYPEFLOW WINDOWS COMPANION

Requires Windows 10/11 and Python 3.10 or newer with Tkinter.
Install Python from https://www.python.org/downloads/windows/ if needed.

1. Unzip this folder. Double-click Start-TypeFlow.cmd.
2. Keep the companion window open. Tick Allow TypeFlow to type.
3. Copy the pairing code. In https://typeflow-liard-ten.vercel.app choose
   Type into: Another app / website (Windows), paste the code and Connect.
4. If the browser asks for local network access, allow it for TypeFlow.
5. Paste source text, choose 1–15 seconds, then Start typing.
6. During the countdown, click the destination textbox in your other app/tab.
7. Escape stops typing globally. Changing windows pauses automatically.
   Resume starts a new countdown so you can select the destination again.

The companion types the exact source text at the selected pace, with variation
and sentence/paragraph/long pauses. Studio typo simulation and boost are not
sent to other apps. No form submission or shortcut commands are sent.

Some apps, elevated windows, games, protected or custom editors may not accept
Unicode keyboard input. This helper does not bypass application restrictions.
Confirm the selected destination and test a short phrase before longer text.
Clicking another field in the same window changes the keyboard destination;
avoid moving focus while typing. It cannot verify what the destination accepted.

Privacy: source text is held in memory only, never saved or logged by the
companion. The website may keep your source locally as before. The helper binds
to 127.0.0.1:31965 only. Every request requires a random pairing code and the
exact TypeFlow website origin. A new code is created each launch. No startup
entry, extension, remote service, cloud relay or administrator access is used.
Closing the companion stops it and its local server. Do not share pairing codes.

This is readable Python source, not a signed Windows executable.
