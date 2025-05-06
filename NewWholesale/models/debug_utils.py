import subprocess
import tempfile
import platform
from odoo import fields


class DebugTerminal:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.log_file = tempfile.mktemp(prefix='odoo_debug_')
            cls._instance.terminal_launched = False
        return cls._instance

    def _get_terminal_cmd(self):
        system = platform.system()
        if system == "Linux":
            return f"gnome-terminal -- bash -c 'tail -f {self.log_file}; exec bash'"
        elif system == "Darwin":  # MacOS
            return f"osascript -e 'tell app \"Terminal\" to do script \"tail -f {self.log_file}\"'"
        elif system == "Windows":
            return f"start cmd /k \"type {self.log_file} && pause\""
        return None

    def print_deb(self, message, model=None, method=None):
        timestamp = fields.Datetime.now()
        log_entry = f"[{timestamp}] {model or 'Global'}.{method or ''}: {message}\n"

        with open(self.log_file, 'a') as f:
            f.write(log_entry)

        if not self.terminal_launched:
            cmd = self._get_terminal_cmd()
            if cmd:
                subprocess.Popen(cmd, shell=True)
                self.terminal_launched = True


# Global instance
debug_terminal = DebugTerminal()


def print_deb(message, model=None, method=None):
    """Public function to use throughout your code"""
    debug_terminal.print_deb(message, model, method)