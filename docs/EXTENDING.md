# **Extending Justniffer**  

[HOME](/) [MAN](MAN)

Justniffer can be extended using **external scripts** in three different ways:  
- **Bash Scripts** – Execute a script at every log entry.  
- **Python Functions** – Process logs with a function called on each entry.  
- **Python Handlers** – Implement structured event handling for network traffic advanced analysis.  

Each method offers flexibility depending on the level of customization and control required.  

---

## 🔹 **Extending with a Bash Script**  

Justniffer allows the execution of external scripts using the -e option, which is triggered for every log entry. Instead of being printed, the log is passed to the script via stdin, and the script is responsible for processing the input and printing the output.

### **Usage Example:**  
Run Justniffer with a Bash script for log processing:  
```bash
sudo justniffer -i any -l '%request' -e ./test.sh
```

### **Example Script (`test.sh`)**  
```bash
#!/bin/bash

while IFS= read -r line
do
    # Display log entry with unprintable characters encoded
    echo -e "$line" | cat -v
done

echo "-----------------------------------------------------"
```


This method is ideal for **quick inline processing** of log entries.  

---

## 🔹 **Extending with a Python Function**  

You can process logs using a Python function, where each log entry is passed as a byte string to a specified function (using byte strings instead of regular strings allows the function to handle binary content as well)

### **Usage Example:**  
Run Justniffer with a Python script:  
```bash
sudo justniffer -i any -P ./simple-example.py
```

### **Example Python Function (`simple-example.py`)**  
```python
def app(log: bytes):
    # Decode log, ignore errors, and split into words
    print(log.decode('utf-8', errors='ignore').split())
```


This method is useful for basic log manipulation and text processing. It is more optimized than the Bash script example because it does not spawn a new process for each log entry. Instead, it directly calls the function, with the Python module being imported only once.

---

## 🔹 **Extending with Python Handlers**  

For structured event-driven handling, implement a **Python class** that reacts to different network events.  

### **Interface Definition (`ExchangeBase`)**  

```python
Endpoint = tuple[str, int]
Conn = tuple[Endpoint, Endpoint]

class ExchangeBase:
    # called when the connection SYN sent
    def on_opening(self, conn: Conn, time: float) -> None:
        pass

    # called when the connection is ESTABLISHED
    def on_open(self, conn: Conn, time) -> None:
        pass

    # called when a request is sent (every TCP packet : already defragmented and ordered end deduplicated)
    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        pass

    # called when a response is sent (every TCP packet : already defragmented and ordered end deduplicated)
    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        pass

    # called when the connection is closed (note that if called before the on_open, it means teh connecion has been refusted or filtered)
    def on_close(self, conn: Conn, time: float,  source_ip: str, source_port: int) -> None:
        pass

    # when the sniffer had been interrupted  in the middle of a connection
    def on_interrupted(self) -> None:
        pass

    # when the connection has timed out
    def on_timed_out(self, conn: Conn, time: float) -> None:
        pass

    # called to get the result to be logged, if None, no log will be generated
    def result(self, time: float) -> str | None:
        pass
```

### **Usage Example:**  
    sudo PYTHONPATH=. justniffer -i any  -l "%python(simpletest)" -N

### **Example Python Handler (`simpletest.py`)**
```python
        METHODS = [m.encode() for m in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')]

        class Exchange:
            def __init__(self) -> None:
                self._request = b''
            
            def on_request(self, conn, content: bytes, time: float) -> None:
                # collect all the request content
                self._request+=content

            def result(self) -> str | None:
                for m in METHODS:
                    # check only http protocol
                    if self._request.startswith(m):
                        # print the first line
                        print(self._request.decode(errors='ignore').split('\n')[0])
                        break
                return None
            
        app = Exchange

```


- Handles different connection events:  **opening**, **request**, **response**, and **closing**  
- Can be used to **track and analyze network traffic flows**.  
- Allows **custom processing logic** through method overrides.  

This approach is recommended for **advanced traffic monitoring and structured event handling**.  

A Python project in the `python` folder serves as an example of how to dissect the protocol and extract the necessary information.  

For instance, the TLS extractor retrieves the **SNI (Server Name Indication)**, the **cipher algorithm**, and, in the case of **TLS 1.2**, the **certificate’s common name, issuer, and expiration date**.


