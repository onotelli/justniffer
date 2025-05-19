Here is a README for the `justniffer-cli` package, drawing upon the information provided in the sources:

# justniffer-cli

A command-line interface (CLI) written in Python for interacting with the `justniffer` network protocol analyzer. This CLI aims to simplify the execution of common `justniffer` tasks and simplify its extendibility, such as providing JSON formatted logs.


## How justniffer-cli Works

The `justniffer-cli` is a **Python application** that acts as a **wrapper** for the core `justniffer` binary. It provides a more structured command-line interface and leverages `justniffer`'s Python extensibility to offer enhanced output formats, such as **JSON**. The CLI can check for compatible versions of both `justniffer` (e.g., compatible with version `0.6.7`) and Python (e.g., compatible with version `3.10`) before execution. When capturing live traffic without reading from a file, the CLI may need to execute `justniffer` with superuser privileges and can handle this requirement.

## Features

Through the `justniffer-cli`, you can access various `justniffer` functionalities:
*   **Run Capture or Analyze File:** Specify a network interface (`-i` or `--interface`) to listen on or a pcap file (`-f` or `--filecap`) to read from.
*   **Apply Packet Filters:** Use the `-p` or `--packet-filter` option with `tcpdump` syntax to filter captured packets.
*   **Capture in the Middle:** Enable capturing streams without the initial 3-way handshake using the `-m` or `--capture-in-the-middle` flag.
*   **Select Output Format:** Choose between `text` (the default) or `json` output formats using the `--format` option. The JSON output is handled via a Python handler within `justniffer` triggered by the CLI.

## Installation

To use `justniffer-cli`, the underlying `justniffer` binary must be installed and accessible in your system's PATH. Installation instructions for `justniffer` itself are provided in the sources for Ubuntu and Debian distributions. It typically requires libraries such as `libpcap` and build tools like `autotools`, `make`, `gcc`, and `g++`.

Specific installation steps for `justniffer-cli` are not detailed in the provided sources, but given its Python nature, it would typically be installed as a Python package.

## Usage

The primary command for `justniffer-cli` is `run`.

**Basic Usage (Live Capture with Text Output):**
```bash
justniffer-cli run --interface eth0
```
This will capture traffic on the `eth0` interface and display it in the default text format.

**Analyze a Capture File with JSON Output:**
```bash
justniffer-cli run --filecap /path/to/capture.pcap --format json
```
This command reads packets from `/path/to/capture.pcap` and outputs the analysis in JSON format. Note that when reading from a file, superuser privileges may not be required.

**Apply a Packet Filter:**
```bash
justniffer-cli run --interface eth0 --packet-filter "port 80 or port 443"
```
This captures traffic on `eth0`, but only processes packets destined for or originating from TCP ports 80 or 443, using `tcpdump` filter syntax.

**Capture in the Middle:**
```bash
justniffer-cli run --interface eth0 --capture-in-the-middle --format text
```
This enables capturing streams even if the initial connection handshake was not observed.

For more advanced logging formats and options available in the core `justniffer` (beyond the `text` and `json` formats offered by the CLI wrapper), refer to the original `justniffer` documentation.

## Further Documentation

For detailed information on `justniffer` features, log format keywords, packet filter syntax, and more, please consult the comprehensive `justniffer` documentation.

## Licensing

The underlying `justniffer` tool is licensed under the **GNU General Public License**. The `justniffer-cli` wrapper, being a Python component interacting with `justniffer`, would typically be distributed under a compatible open-source license.