# justniffer-cli

A Python-based command-line interface (CLI) for interacting with [`justniffer`] (https://github.com/onotelli/justniffer). 

`justniffer-cli` simplifies execution of common tasks and enhances extendibility, such as providing JSON-formatted logs.

## How justniffer-cli Works

`justniffer-cli` serves as a **wrapper** for the `justniffer` binary, offering a structured command-line interface with configurable settings. Leveraging `justniffer`'s Python extensibility, it supports enhanced output formats like **JSON**.

Compatible versions:
- `justniffer` **>= 0.6.7**
- Python **>= 3.10**

## Features

With `justniffer-cli`, you can:
- **Capture Live Traffic or Analyze a File:** Use `-i`/`--interface` for live capture or `-f`/`--filecap` to read from a `.pcap` file.
- **Apply Packet Filters:** Utilize `tcpdump` syntax via `-p`/`--packet-filter` to refine captured data.
- **Capture Mid-Session Traffic:** Use `-m`/`--capture-in-the-middle` to record streams missing the initial handshake.
- **Choose Output Format:** Set `--formatter` to `text` (default) or `json` for structured data output.

## Installation

Make sure `justniffer` is installed and accessible in your system's PATH. Refer to the official [`justniffer` README](https://github.com/onotelli/justniffer) for detailed installation instructions.

## Usage

### Live Capture with Default Text Output:
```bash
justniffer-cli run --interface eth0
```

Output:

```
2025-05-21 00:04:26.489317 b710573dce68be87 continue - 16 192.168.1.112:41352 20.42.65.88:443 - 2.0831 2.1948 - 10.7247 47.4229 9164 94 TLS mobile.events.data.microsoft.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:39.408867 b710573dce68be87 continue - 17 192.168.1.112:41352 20.42.65.88:443 - 0.0608 0.1756 - 0.0017 58.4735 4698 137 TLS mobile.events.data.microsoft.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:39.841406 03dd2b37229901c1 started - 1 192.168.1.112:52148 13.107.5.93:443 0.0299 0.0000 0.0289 0.0005 0.0016 0.0593 517 99 TLS default.exp-tas.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:39.871901 03dd2b37229901c1 continue - 2 192.168.1.112:52148 13.107.5.93:443 - 0.0000 0.0316 - 0.0174 0.0932 344 4178 TLS default.exp-tas.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:02:11.978878 3df487d9a24df0b5 closed client 2 192.168.1.112:33254 151.101.0.223:443 - 0.0000 148.0465 - 0.0000 148.0838 64 24 TLS analytics.python.org TLS_1_3 TLS_AES_128_GCM_SHA256 - - -
2025-05-21 00:04:40.035757 1b1695e6ee179d18 started - 1 192.168.1.112:34262 2.19.198.66:443 0.0245 0.0000 0.0291 0.0013 0.0006 0.0549 2127 270 TLS easylist-downloads.adblockplus.org TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:40.095893 f859fb72ac50f753 started - 1 192.168.1.112:58712 20.189.172.33:443 0.1708 0.0000 0.1723 0.0004 0.0039 0.3436 517 99 TLS westus-0.in.applicationinsights.azure.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:40.272120 f859fb72ac50f753 continue - 2 192.168.1.112:58712 20.189.172.33:443 - 0.0000 0.1748 - 0.0032 0.5223 446 4409 TLS westus-0.in.applicationinsights.azure.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:40.450092 f859fb72ac50f753 continue - 3 192.168.1.112:58712 20.189.172.33:443 - 0.0000 0.1709 - 0.0271 0.6972 298 479 TLS westus-0.in.applicationinsights.azure.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:40.648988 f859fb72ac50f753 closed server 4 192.168.1.112:58712 20.189.172.33:443 - 0.0000 - - - 0.8943 24 0 TLS westus-0.in.applicationinsights.azure.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:29.031771 9316fc4174e5eda3 continue - 10 192.168.1.112:43254 35.223.238.178:443 - 0.0000 0.1265 - 12.4223 41.4833 750 325 TLS server.codeium.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00:04:37.755782 3d8e991c5cafa438 closed client 3 192.168.1.112:52124 13.107.5.93:443 - 0.0000 0.0472 - 4.0331 4.2584 607 4772 TLS default.exp-tas.com TLS_1_3 TLS_AES_256_GCM_SHA384 - - -
2025-05-21 00

```



### Analyze a Capture File with JSON Output:
```bash
justniffer-cli run --filecap /path/to/capture.pcap --formatter json
```
Superuser privileges are typically unnecessary when reading from a file.

### Apply a Packet Filter:
```bash
justniffer-cli run --interface eth0 --packet-filter "port 80 or port 443"
```
Filters traffic to TCP ports **80** or **443**, using `tcpdump` syntax.

### Capture Mid-Session Streams:
```bash
justniffer-cli run --interface eth0 --capture-in-the-middle --formatter text
```
Records network streams even if the handshake was missed

# Justniffer Configuration Guide

Configuration is primarily managed through a YAML file, allowing for flexible customization of protocol selectors, data extractors, and output formatting. Navigate through the sections using the sidebar to learn more about each aspect of the configuration.

The goal is to provide an easy way to understand and reference the various configuration options available in Justniffer.

## 1. Configuration File Overview

`justniffer-cli` uses a YAML file for its main configuration. The path to this file can be specified:

* Via the `--config-filepath` command-line argument when running `justniffer-cli`.

* Through the `JUSTNIFFER_CONFIG_FILE` environment variable.

The configuration file supports the following top-level keys:

* `extractors`: Defines a list of data extractors.

* `formatter`: Specifies the output formatter.

If no configuration file is provided, `justniffer-cli` will use default settings for extractors and formatter.

```yaml
# Basic YAML Structure
extractors:
  # ... extractor definitions
formatter: # ... formatter definition


```

## 2. Extractors

Extractors are components that pull specific pieces of information from network connections, events, and content.

* **Definition**: Under the `extractors` key in the YAML file.

* **Format**: A list (or tuple) of extractor definitions, similar to selectors:

  * A string: The class name of the extractor.

  * A dictionary: The key is the extractor's class name, and the value is a dictionary of constructor arguments.

* **Default Extractors**: If `extractors` is not defined in the configuration, a predefined set of extractors is used. This set includes:

  * `RequestTimestamp`, `ConnectionID`, `ConnectionState`, `CloseOriginator`, `ConnectionRequests`, `SourceIPPort`, `DestIPPort`, `ConnectionTime`, `RequestTime`, `ResponseTime`, `Idle1Time`, `Idle2Time`, `ConnectionDuration`, `RequestSize`, `ResponseSize`, `ProtocolSelector` (which in turn uses the configured `selectors`).

* **Types of Extractors**:

  * `Extractor`: Base for general data extraction from connection metadata and events.

  * `ContentExtractor`: Base for extractors that operate on the raw request and response content bytes.

  * `TypedContentExtractor`: A generic version of `ContentExtractor` for better type safety.

* **Custom Extractors**: Add custom extractors by specifying their class names (e.g., `test_extractors.tests:TestExtractor`).

### Selectors

Selectors are key components of the `ProtocolSelector`, responsible for identifying and parsing specific network protocols (e.g., TLS, HTTP, SSH) from captured network traffic. By inspecting the content of network streams, selectors determine the protocol of a given connection and extract relevant information.

* **Definition**: Under the `selectors` key in the YAML file.

* **Format**: A list (or tuple) of selector definitions. Each item can be:

  * A string: The class name of the selector (e.g., `TLSInfoExtractor`). Assumed to be in the `justniffer.handlers` module unless a full path is given.

  * A dictionary: The key is the selector's class name, and the value is a dictionary of arguments to be passed to its constructor.

* **Default Selectors**: If not specified, the defaults are:

  * `TLSInfoExtractor`

  * `HttpInfoExtractor`

  * `SSHInfoExtractor`

* **Custom Selectors**: To use a custom selector, provide its class name. If the class resides in a different module, use the format `your_module_name:YourSelectorClass`.

### Example YAML:

```yaml
extractors:
  ConnectionID:
  SourceIPPort:
  DestIPPort:
  ResponseSize:
  test_extractors.tests:TestExtractor: # Example of a custom content extractor
      parameter_a: "value_x" # Arguments are passed as keyword arguments to TestExtractor
      parameter_b: 100
  ProtocolSelector:
    selectors:
      TLSInfoExtractor:
      HttpInfoExtractor:
      SSHInfoExtractor:
      PlainTextExtractor:
        length: 20
      my_custom_module:MyCustomProtocolSelector: # Example of a custom selector
      my_custom_module2:AnotherSelectorWithOptions: # Example of a selector with arguments
        option1: true
        threshold: 42

```

## 3. Formatter

Formatters control the output format of the data collected by the extractors.

* **Definition**: Specified under the `formatter` key in the YAML file. This can also be set via the `JUSTNIFFER_FORMATTER` environment variable or the `--formatter` command-line argument (CLI argument takes highest precedence, then environment variable, then config file).

* **Format**:

  * A string: The name of the formatter (e.g., `"json"`, `"str"`).

  * A dictionary: The key is the formatter name, and the value is a dictionary of arguments for its constructor.

* **Built-in Formatters**:

  * `str`: (Default if no other formatter is specified) Formats output as a string with fields separated by a delimiter.

    * Constructor arguments: `sep` (default: `" "`), `null_value` (default: `"-"`).

  * `json`: Formats output as a JSON string.

* **Custom Formatters**: Use custom formatters by providing their class name (e.g., `my_formatter_module:MyAdvancedFormatter`).

* **Default Formatter**: If no formatter is explicitly configured, `StrFormatter` is used.

### Example YAML for Formatter:

#### JSON Formatter Example:

```yaml
formatter: json


```

#### String Formatter (Custom) Example:

```yaml
formatter:
  str:
    sep: "; "
    null_value: "N/A"


```

#### Custom Formatter Example:

```yaml
formatter: my_custom_formatters:SpecialReportFormatter

```



## Licensing

 **GPL v3**


