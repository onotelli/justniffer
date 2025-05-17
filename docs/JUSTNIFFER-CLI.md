# justniffer-cli

`justniffer-cli` is a **Python wrapper** around the `justniffer` command-line tool. Its purpose is to provide a **more accessible and potentially faster way to develop protocol analyzers in Python**. It achieves this by utilizing `justniffer`'s capability to extend its functionality via Python.

`justniffer-cli` essentially prepares and executes the `justniffer` command with options that direct `justniffer` to use specific Python code (referred to as handlers or functions) for processing the captured network traffic. This allows developers to work within the Python environment for analysis logic, building upon the robust TCP flow rebuilding provided by `justniffer`.

Key aspects and functionalities of `justniffer-cli` based on the sources include:

*   **Wrapper for `justniffer`**: It acts as an interface to the core `justniffer` binary.
*   **Leverages Python Extensibility**: It specifically uses `justniffer`'s `-l "%python(...)"` format option to execute Python code for handling captured data. `justniffer` supports executing external scripts (like Bash or Python functions) or implementing structured event handling via Python classes (handlers). The CLI implementation seems to utilize Python handlers defined within the `justniffer.handlers` module.
*   **Facilitates Protocol Analysis Development**: By abstracting the direct `justniffer` command line usage and providing a Python environment, it aims to simplify the process of creating custom protocol analyzers. The underlying `justniffer` tool is designed to handle complex low-level TCP/IP issues like IP fragmentation, TCP retransmission, and reordering, providing a reliable TCP flow.
*   **Input Sources**: It can capture traffic directly from a **network interface** (`-i`, `--interface`) or read from a previously saved **packet capture file** in `tcpdump` format (`-f`, `--filecap`). Interface autocompletion is available.
*   **Packet Filtering**: Allows applying a **packet filter** (`-p`, `--packet-filter`) using `tcpdump` syntax to limit the traffic being processed.
*   **Capture in the Middle**: Supports capturing packets even without the initial connection handshake (`-m`, `--capture-in-the-middle`), although this may produce unexpected results.
*   **Output Format**: Supports specifying the output format, such as `json` or `text`. This formatting is handled by internal formatters within the Python code executed by `justniffer`.
*   **Python Handlers (`ExchangeBase`)**: The underlying Python extensibility model used involves implementing a **Python class** that reacts to different network events. An `ExchangeBase` class defines methods like `on_opening`, `on_open`, `on_request`, `on_response`, `on_close`, `on_interrupted`, `on_timed_out`, and `result` which are called at different stages of a TCP connection lifecycle.
*   **Version Compatibility Check**: `justniffer-cli` checks for compatible versions of both `justniffer` and Python before execution.
*   **Sudo Requirement**: Capturing traffic from a network interface typically requires root privileges, so `justniffer-cli` uses `sudo` when necessary.
*   **Protocol Parsing**: The Python handlers executed by the CLI include logic to parse and extract information from different protocols, such as **TLS** and **HTTP**.

In essence, `justniffer-cli` simplifies the interaction with `justniffer`, particularly for Python developers, enabling them to focus on the logic of analyzing protocols and data streams using Python's capabilities, while `justniffer` handles the complexities of capturing and rebuilding TCP traffic.