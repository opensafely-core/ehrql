"""
Initialize and provide a thin wrapper around a pyright language server

The initialization dance was inferred from the source code of the pyright
playground client:
https://github.com/erictraut/pyright-playground/blob/main/server/src/lspClient.ts

Another good resource is the specification for the Language Server Protocol:
https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification)
though it's a bit hard to navigate.
"""

import json
import os
import re
import sys
from pathlib import Path
from subprocess import PIPE, Popen


class LanguageServer:
    def __init__(self, temp_file_path: Path):
        self._message_id = 0

        # The pyright-langserver needs the ehrql repo directory on
        # PYTHONPATH so it can understand ehrql, and it needs the current
        # location of the python executable (also where pyright-langserver)
        # is on its PATH variable
        env = os.environ.copy()
        env["PYTHONPATH"] = Path("").absolute().as_uri()
        env["PATH"] = os.path.dirname(sys.executable)

        self._language_server = Popen(
            ["pyright-langserver", "--stdio"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            env=env,
        )
        # Server immediately emits two log messages:
        #   {'method': 'window/logMessage', 'params': { 'message': 'Pyright language server 1.1.396 starting'}}
        #   {'method': 'window/logMessage', 'params': { 'message': 'Server root directory: file:...'}}
        self._read_messages(2)

        # Send an "initialize" message
        self._send_message(
            "initialize",
            {
                "processId": os.getpid(),
                "rootUri": Path("").absolute().as_uri(),
                "capabilities": {
                    "textDocument": {
                        "hover": {
                            # Can also pass in "markdown" in this list as well as "plaintext"
                            # markdown is what vscode uses, but for testing purposes it's
                            # slightly easier to compare the plain text results
                            "contentFormat": ["plaintext"],
                        },
                    },
                },
            },
        )

        # Confirm with "initialized" notification
        self._send_notification("initialized", {})
        # Need to _send these notification as well
        self._send_notification("workspace/didChangeConfiguration", {})

        # Now we create a temp file which we will amend in each test and then
        # call the language server to get completions. For reasons I can't quite
        # figure out, the initial content needs to have a second, non-empty line
        # otherwise some of the tests fail
        self.open_doc(temp_file_path, "Line 1\nLine 2")

        # Server now emits a number of "window/logMessage" messages (was 6 prior to
        # pyright v1.1.393, but is now 7), finishing with a
        # "textDocument/publishDiagnostics" message. So we read the messages until
        # we get to that one.
        self._read_until_specific_method("textDocument/publishDiagnostics")

        # The server is now ready for completion and hover requests

    def _next_id(self):
        self._message_id += 1
        return self._message_id

    def get_completion_results_from_file(self, line, cursor_position):
        """
        For a given line and cursor_position returns the list of potential
        completion results. This assumes that the file is already loaded by
        the language server (via `open_doc`). If you want to test a single line
        of code, then use the `get_completion_results()` method instead
        """
        completion_response = self._get_completion(line, cursor_position)
        results = completion_response.get("result")
        items = results.get("items")
        return items

    def get_completion_results(
        self, text_for_completion, cursor_position=None
    ):  # pragma: no cover
        """
        For a given string of text provide the list of potential completion
        results. If cursor_position is omitted, then it looks for completion
        at the end of the text provided.

        To use, you should provide the entire file contents up to the point
        that you want to check autocomplete. It should all be on a single
        line, with ';' separators.

        Returns a list of completion items which look like this:
        { "label": str, "kind": CompletionKind, "sortText": str}
        """
        self._notify_document_change(0, text_for_completion)

        if cursor_position is None:
            cursor_position = len(text_for_completion)

        return self.get_completion_results_from_file(0, cursor_position)

    def get_element_type_from_file(self, line, cursor_position):
        """
        For a given line and cursor_position returns the type of the currently
        hovered piece of text. This assumes that the file is already loaded by
        the language server (via `open_doc`). If you want to test a single line
        of code, then use the `get_element_type()` method instead
        """
        hover_response = self._get_hover_text(line, cursor_position)
        value = hover_response.get("result").get("contents").get("value")
        first_line = value.split("\n\n")[0]

        # First line contains the signature like `(variable) name: type`
        variable_signature = re.search(
            "^\\((?:variable|property)\\) (?P<var_name>[^:]+): (?P<type>.+)",
            first_line,
        )

        # First line contains the signature like `(method) def method_name() -> type`
        method_signature = re.search(
            "^\\(method\\) def (?P<method_name>[^(]+)\\([^()]*\\) -> (?P<type>.+)",
            first_line,
        )

        if variable_signature:
            thing_type = variable_signature.group("type")
        elif method_signature:
            thing_type = method_signature.group("type")
        else:  # pragma: no cover
            assert 0, (
                f"The type signature `{value}` could not be parsed by self._language_server.py."
            )

        return thing_type

    def get_element_type(self, text, cursor_position=None):  # pragma: no cover
        """
        For a given string of text provide the inferred type of the item at the
        current cursor_position. If cursor_position is omitted, it assumes the
        thing to check is the last thing typed and so looks at the cursor position
        just before the end of the string.

        To use, you should provide the entire file contents up to the point
        that you want to get the type. It should all be on a single
        line, with ';' separators.
        """
        self._notify_document_change(0, f"{text}\n")

        if cursor_position is None:
            cursor_position = len(text) - 1

        return self.get_element_type_from_file(0, cursor_position)

    def _notify_document_change(self, line_number, new_text):  # pragma: no cover
        # Need to update text_document version
        self._text_document["version"] = f"v{self._next_id()}"
        self._send_notification(
            "textDocument/didChange",
            {
                "textDocument": self._text_document,
                "contentChanges": [
                    {
                        "range": {
                            "start": {"line": line_number, "character": 0},
                            "end": {
                                "line": line_number,
                                "character": len(new_text),
                            },
                        },
                        "text": new_text,
                    }
                ],
            },
        )
        # This notification causes a response to be sent, so we
        # need to read it to clear it from stdout
        self._read_message()

    def _get_completion(self, line_number, character):
        """
        Get the list of completion objects for a given position
        """
        return self._send_message(
            "textDocument/completion",
            {
                "textDocument": self._text_document,
                "position": {"line": line_number, "character": character},
            },
        )

    def _get_hover_text(self, line_number, character):
        """
        Get the inferred type
        """
        return self._send_message(
            "textDocument/hover",
            {
                "textDocument": self._text_document,
                "position": {"line": line_number, "character": character},
            },
        )

    def _read_message(self):
        """
        Read a message from the language server.

        Message format is a header like "Content-Length: xxx", followed by
        \r\n\r\n then the message in JSON RPC.
        """
        line = self._language_server.stdout.readline().decode("utf-8").strip()
        while not line.startswith("Content-Length:"):  # pragma: no cover
            line = self._language_server.stdout.readline().decode("utf-8").strip()
        content_length = int(line.split(":")[1].strip())
        content = self._language_server.stdout.read(content_length + 2).decode("utf-8")
        return json.loads(content)

    def _read_messages(self, number_of_messages=1):
        """Read multiple messages from the language server"""
        messages = []
        while number_of_messages > 0:
            messages.append(self._read_message())
            number_of_messages -= 1
        return messages

    def _read_until_specific_method(self, method):
        """Reads messages from the server until we get the one we're looking for"""
        messages = [self._read_message()]
        while messages[-1]["method"] != method:
            messages.append(self._read_message())
        return messages

    def _send(self, message):
        content = json.dumps(message)
        message_str = f"Content-Length: {str(len(content))}\r\n\r\n{content}"
        self._language_server.stdin.write(message_str.encode())
        self._language_server.stdin.flush()

    def _send_notification(self, method, params):
        """Send a notification to the language server - there is no response."""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        self._send(notification)

    def _send_message(self, method, params):
        """Send a message to the language server and return the response."""
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params,
        }
        self._send(message)
        return self._read_message()

    def open_doc(self, temp_file_path, content):
        """
        Tell the language server about a file we have "opened" so that
        it can parse it to make the autocomplete responses faster
        """
        temp_file_path.write_text(content, encoding="utf-8")
        temp_file_uri = temp_file_path.absolute().as_uri()

        self._text_document = {
            "uri": temp_file_uri,
            "languageId": "python",
            "version": 1,
            "text": content,
        }
        self._send_notification(
            "textDocument/didOpen",
            {"textDocument": self._text_document},
        )

        self._read_message()
