import importlib.util
import io
import json
import pathlib
import sys
import unittest

path = pathlib.Path(__file__).parents[1] / 'companion/windows/typeflow_companion.py'
spec = importlib.util.spec_from_file_location('typeflow_companion', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Keyboard:
    def __init__(self):
        self.typed = []
        self.window = 123
        self.window_title = 'A text editor'
        self.escaped = False
        self.change_after = None
    def escape(self): return self.escaped
    def modifiers(self): return False
    def foreground(self):
        return 456 if self.change_after is not None and len(self.typed) >= self.change_after else self.window
    def title(self, hwnd): return self.window_title
    def type_character(self, c): self.typed.append(c)

def settings():
    return {'wpm':240,'variation':0,'sentence':0,'paragraph':0,'longEvery':0,'longPause':500,'countdown':1}

class CompanionTests(unittest.TestCase):
    def test_input_validation_and_explicit_enable(self):
        for body in ({'text':''},{'text':'ok','settings':[]},{'text':'ok','settings':{'countdown':0}},{'text':'ok','settings':{'countdown':16}},{'text':'ok','settings':{'wpm':float('inf')}}):
            with self.assertRaises(ValueError): m.validate_session(body)
        with self.assertRaisesRegex(ValueError, 'Enable'):
            m.Session(Keyboard()).start({'text':'A','settings':settings()})
    def test_exact_unicode_output_and_memory_cleanup(self):
        keyboard=Keyboard(); session=m.Session(keyboard); session.allowed=True
        session.start({'text':'A😀é','settings':settings()}); session.thread.join(4)
        self.assertEqual(''.join(keyboard.typed),'A😀é')
        self.assertEqual(session.status,'Complete'); self.assertEqual(session.text,'')
        self.assertEqual(session.snapshot()['total'],3)
    def test_escape_cancels_during_countdown(self):
        keyboard=Keyboard(); keyboard.escaped=True; session=m.Session(keyboard); session.allowed=True
        session.start({'text':'ABC','settings':settings()}); session.thread.join(2)
        self.assertEqual(keyboard.typed,[]); self.assertEqual(session.status,'Stopped')
    def test_focus_change_pauses_then_resume_uses_new_countdown(self):
        keyboard=Keyboard(); keyboard.change_after=1; session=m.Session(keyboard); session.allowed=True
        session.start({'text':'ABC','settings':settings()}); session.thread.join(3)
        self.assertEqual(keyboard.typed,['A']); self.assertEqual(session.status,'Paused')
        keyboard.change_after=None; keyboard.window=789
        session.start(resume=True); self.assertEqual(session.status,'Countdown'); session.thread.join(4)
        self.assertEqual(''.join(keyboard.typed),'ABC'); self.assertEqual(session.status,'Complete')
    def test_source_window_is_not_a_valid_destination(self):
        keyboard=Keyboard(); keyboard.window_title='TypeFlow — Your words, in motion'; session=m.Session(keyboard); session.allowed=True
        session.start({'text':'ABC','settings':settings()}); session.thread.join(3)
        self.assertEqual(keyboard.typed,[]); self.assertEqual(session.status,'Stopped')
    def test_pairing_requires_exact_origin_host_and_secret(self):
        session=m.Session(Keyboard()); cls=m.handler_for(session); handler=cls.__new__(cls)
        handler.headers={'Origin':'https://typeflow-liard-ten.vercel.app','Host':'127.0.0.1:31965','Authorization':'Bearer '+session.token}
        self.assertTrue(handler._authorized())
        for key,value in [('Origin','https://evil.example'),('Host','evil.example:31965'),('Authorization','Bearer wrong')]:
            before=handler.headers[key];handler.headers[key]=value
            self.assertFalse(handler._authorized());handler.headers[key]=before
    @unittest.skipUnless(sys.platform=='win32','Windows ABI only')
    def test_windows_input_abi_without_sending_any_input(self):
        keyboard=m.WindowsKeyboard()
        self.assertEqual(m.ctypes.sizeof(keyboard.INPUT),40 if m.ctypes.sizeof(m.ctypes.c_void_p)==8 else 28)

if __name__=='__main__': unittest.main()
