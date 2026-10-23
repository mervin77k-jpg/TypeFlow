"""TypeFlow Windows Companion. Standard-library only; no installation, cloud, or telemetry."""
import ctypes
from ctypes import wintypes
import json
import math
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = '127.0.0.1'
PORT = 31965
ALLOWED_ORIGINS = {'https://typeflow-liard-ten.vercel.app'}
MAX_BODY = 700000

def validate_session(body):
    text = body.get('text')
    if not isinstance(text, str) or not text.strip() or len(text) > 100000:
        raise ValueError('Source text must contain 1–100,000 characters.')
    raw = body.get('settings', {})
    if not isinstance(raw, dict):
        raise ValueError('Invalid settings.')
    bounds = {'wpm': (10, 240, 65), 'variation': (0, 80, 20), 'sentence': (0, 3000, 650), 'paragraph': (0, 5000, 1200), 'longEvery': (0, 150, 35), 'longPause': (500, 10000, 2500), 'countdown': (1, 15, 3)}
    settings = {}
    for key, (low, high, default) in bounds.items():
        n = raw.get(key, default)
        if isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or not low <= n <= high:
            raise ValueError(f'Invalid {key}.')
        settings[key] = n
    settings['countdown'] = int(settings['countdown'])
    settings['longEvery'] = int(settings['longEvery'])
    return text.replace('\r\n', '\n').replace('\r', '\n'), settings

class WindowsKeyboard:
    def __init__(self):
        if sys.platform != 'win32':
            raise RuntimeError('This companion requires Windows.')
        self.user = ctypes.WinDLL('user32', use_last_error=True)
        self.user.GetForegroundWindow.restype = wintypes.HWND
        self.user.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.user.GetAsyncKeyState.restype = ctypes.c_short
        self.user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.user.GetWindowTextW.restype = ctypes.c_int
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [('wVk', wintypes.WORD), ('wScan', wintypes.WORD), ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t)]
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG), ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t)]
        class HARDWAREINPUT(ctypes.Structure):
            _fields_ = [('uMsg', wintypes.DWORD), ('wParamL', wintypes.WORD), ('wParamH', wintypes.WORD)]
        class UNION(ctypes.Union):
            _fields_ = [('ki', KEYBDINPUT), ('mi', MOUSEINPUT), ('hi', HARDWAREINPUT)]
        class INPUT(ctypes.Structure):
            _anonymous_ = ('u',)
            _fields_ = [('type', wintypes.DWORD), ('u', UNION)]
        self.INPUT, self.KEYBDINPUT = INPUT, KEYBDINPUT
        self.user.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
        self.user.SendInput.restype = wintypes.UINT
    def escape(self):
        return bool(self.user.GetAsyncKeyState(0x1B) & 0x8000)
    def modifiers(self):
        return any(self.user.GetAsyncKeyState(vk) & 0x8000 for vk in (0x10, 0x11, 0x12, 0x5B, 0x5C))
    def foreground(self):
        return self.user.GetForegroundWindow()
    def title(self, hwnd):
        buf = ctypes.create_unicode_buffer(1024)
        self.user.GetWindowTextW(hwnd, buf, len(buf))
        return buf.value
    def type_character(self, character):
        # Unicode input only: never issue clipboard, shortcut, Tab or Enter virtual-key commands.
        encoded = character.encode('utf-16-le')
        events = []
        for i in range(0, len(encoded), 2):
            unit = int.from_bytes(encoded[i:i+2], 'little')
            for flags in (0x0004, 0x0004 | 0x0002):
                item = self.INPUT(type=1)
                item.ki = self.KEYBDINPUT(0, unit, flags, 0, 0)
                events.append(item)
        array = (self.INPUT * len(events))(*events)
        if self.user.SendInput(len(events), array, ctypes.sizeof(self.INPUT)) != len(events):
            raise RuntimeError('Windows blocked input to this application. Try an ordinary non-elevated text editor.')

class Session:
    def __init__(self, keyboard, token=None):
        self.keyboard = keyboard
        self.token = token or secrets.token_urlsafe(32)
        self.allowed = False
        self.lock = threading.RLock()
        self.status, self.message = 'Ready', 'Enable external typing in this window, then pair the website.'
        self.text, self.settings = '', {}
        self.position, self.remaining, self.elapsed, self.total = 0, 0, 0, 0
        self.cancel = threading.Event()
        self.thread = None
        self.target = None
    def snapshot(self):
        with self.lock:
            return {'status': self.status, 'message': self.message, 'position': self.position, 'total': self.total, 'countdown': self.remaining, 'elapsed': self.elapsed, 'corrections': 0, 'allowed': self.allowed}
    def stop(self):
        self.cancel.set()
        with self.lock:
            self.status, self.message = 'Stopped', 'Stopped. No further input will be sent.'
    def pause(self):
        self.cancel.set()
        with self.lock:
            self.status, self.message = 'Paused', 'Paused. Resume starts a new countdown so you can choose the destination again.'
    def start(self, body=None, resume=False):
        with self.lock:
            if not self.allowed:
                raise ValueError('Enable external typing in the companion window first.')
            if self.thread and self.thread.is_alive():
                if not self.cancel.is_set():
                    raise ValueError('A typing session is already running.')
                self.thread.join(timeout=0.1)
                if self.thread.is_alive():
                    raise ValueError('Please wait for the previous session to stop.')
            if not resume:
                self.text, self.settings = validate_session(body)
                self.position, self.elapsed = 0, 0
                self.total = len(self.text)
            elif self.status != 'Paused' or not self.text:
                raise ValueError('There is no paused session to resume.')
            self.cancel = threading.Event()
            self.status, self.message = 'Countdown', 'Click the destination textbox now. Escape cancels.'
            self.remaining = self.settings['countdown']
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    def _wait(self, seconds, check_target=True):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if self.cancel.is_set():
                return False
            if self.keyboard.escape():
                self.stop()
                return False
            if check_target and self.target and self.keyboard.foreground() != self.target:
                self.pause()
                self.message = 'Paused because the destination window changed. Resume, then refocus the intended textbox.'
                return False
            time.sleep(min(0.02, max(0, deadline-time.monotonic())))
        return not self.cancel.is_set()
    def _run(self):
        import random
        try:
            deadline = time.monotonic() + self.settings['countdown']
            while time.monotonic() < deadline:
                self.remaining = max(0, math.ceil(deadline-time.monotonic()))
                if not self._wait(min(0.05, max(0, deadline-time.monotonic())), False):
                    return
            self.remaining = 0
            self.target = self.keyboard.foreground()
            if not self.target or 'typeflow' in self.keyboard.title(self.target).casefold():
                self.status, self.message = 'Stopped', 'No external destination selected. Click another textbox during the countdown and try again.'
                return
            started, previous = time.monotonic(), self.elapsed
            self.status, self.message = 'Typing', 'Typing into the selected window. Escape stops; changing windows pauses.'
            while self.position < len(self.text):
                if not self._wait(0.001):
                    return
                if self.keyboard.modifiers():
                    if not self._wait(0.03):
                        return
                    continue
                # Recheck focus immediately before each input event. Do not follow window changes.
                if self.keyboard.foreground() != self.target:
                    self.pause()
                    return
                character = self.text[self.position]
                self.keyboard.type_character(character)
                self.position += 1
                self.elapsed = previous + time.monotonic() - started
                cfg = self.settings
                delay = 60/(cfg['wpm']*5) * (1+(random.random()*2-1)*cfg['variation']/100)
                if character == '\n':
                    delay += cfg['paragraph']/1000
                elif character in '.!?':
                    delay += cfg['sentence']/1000
                if cfg['longEvery'] and self.position % (int(cfg['longEvery'])*5) == 0:
                    self.status = 'Thinking'
                    delay += cfg['longPause']/1000
                if not self._wait(delay):
                    return
                self.status = 'Typing'
            self.status, self.message = 'Complete', 'Finished sending the source text. Check the destination; application support varies.'
        except Exception as exc:
            self.cancel.set()
            self.status, self.message = 'Stopped', str(exc)
        finally:
            # Text is kept in memory only. Clear it after a completed or stopped session.
            if self.status in ('Complete', 'Stopped'):
                self.text = ''

def handler_for(session):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Never log pairing codes or source text.
        def _origin(self):
            return self.headers.get('Origin') in ALLOWED_ORIGINS and self.headers.get('Host') == f'{HOST}:{PORT}'
        def _reply(self, status, data):
            payload = json.dumps(data).encode()
            self.send_response(status)
            origin = self.headers.get('Origin')
            if origin in ALLOWED_ORIGINS:
                self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        def do_OPTIONS(self):
            self._reply(200 if self._origin() else 403, {})
        def _authorized(self):
            token = self.headers.get('Authorization', '')
            return self._origin() and secrets.compare_digest(token, 'Bearer '+session.token)
        def do_GET(self):
            if not self._authorized():
                return self._reply(403, {'error': 'Pairing authorization required.'})
            if self.path != '/status':
                return self._reply(404, {'error': 'Not found'})
            self._reply(200, session.snapshot())
        def do_POST(self):
            if not self._authorized():
                return self._reply(403, {'error': 'Pairing authorization required.'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 <= length <= MAX_BODY:
                    return self._reply(413, {'error': 'Request too large.'})
                body = json.loads(self.rfile.read(length) or b'{}')
                if not isinstance(body, dict):
                    raise ValueError('Invalid request.')
                if self.path == '/start':
                    session.start(body)
                elif self.path == '/resume':
                    session.start(resume=True)
                elif self.path == '/pause':
                    session.pause()
                elif self.path == '/stop':
                    session.stop()
                else:
                    return self._reply(404, {'error': 'Not found'})
                self._reply(200, session.snapshot())
            except (ValueError, TypeError, OverflowError) as exc:
                self._reply(400, {'error': str(exc)})
    return Handler

def main():
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk()
    root.title('TypeFlow Companion')
    root.geometry('620x420')
    session = Session(WindowsKeyboard())
    try:
        server = ThreadingHTTPServer((HOST, PORT), handler_for(session))
    except OSError:
        messagebox.showerror('TypeFlow', 'The companion may already be running, or port 31965 is unavailable.')
        root.destroy()
        return
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='TypeFlow · Windows Companion', font=('Segoe UI', 17, 'bold')).pack(anchor='w')
    ttk.Label(frame, text='Keep this window open. Your text stays on this computer.').pack(anchor='w', pady=(8, 18))
    ttk.Label(frame, text='Pairing code (changes every time this app opens):').pack(anchor='w')
    code = ttk.Entry(frame)
    code.insert(0, session.token)
    code.configure(state='readonly')
    code.pack(fill='x', pady=8)
    def copy():
        root.clipboard_clear()
        root.clipboard_append(session.token)
    ttk.Button(frame, text='Copy pairing code', command=copy).pack(anchor='w')
    enabled = tk.BooleanVar(value=False)
    def allow():
        session.allowed = enabled.get()
        if not session.allowed:
            session.stop()
    ttk.Checkbutton(frame, text='Allow TypeFlow to type into the textbox I choose', variable=enabled, command=allow).pack(anchor='w', pady=18)
    state = tk.StringVar()
    ttk.Label(frame, textvariable=state, wraplength=560).pack(anchor='w', pady=8)
    ttk.Button(frame, text='Stop typing', command=session.stop).pack(anchor='w')
    ttk.Label(frame, text='Esc stops anywhere. Switching windows pauses. Never runs at startup.', wraplength=560).pack(anchor='w', pady=14)
    def update():
        d = session.snapshot()
        state.set((f"Starting in {d['countdown']}…" if d['status']=='Countdown' else d['status'])+'\n'+d['message'])
        root.after(150, update)
    def close():
        session.stop()
        server.shutdown()
        server.server_close()
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', close)
    update()
    root.mainloop()

if __name__ == '__main__':
    main()


