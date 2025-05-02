# **Extending Justniffer**  

Justniffer can be extended using **external scripts** in three different ways:  
- **Bash Scripts** – Execute a script at every log entry.  
- **Python Functions** – Process logs with a function called on each entry.  
- **Python Handlers** – Implement structured event handling for network traffic.  

Each method offers flexibility depending on the level of customization and control required.  

---

## 🔹 **Extending Justniffer with a Bash Script**  

Justniffer allows calling external executable scripts using the `-e` option, which is triggered at every log entry.  

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

## 🔹 **Extending Justniffer with a Python Function**  

You can process logs using a **Python function**, where each log entry is passed as a byte string to a specified function.  

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

### **Explanation:**  

This method is useful for **basic log manipulation and text processing**.  

---

## 🔹 **Extending Justniffer with Python Handlers**  

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
    def on_close(self, conn: Conn, time: float) -> None:
        pass

    # when the sniffer had been interrupted  in the middle of a connection
    def on_interrupted(self) -> None:
        pass

    # when the connection has timed out
    def on_timed_out(self, conn: Conn, time: float) -> None:
        pass

    # called to get the result to be logged, if None, no log will be generated
    def result(self) -> str | None:
        pass
```

### **Usage Example:**  
    sudo justniffer -i any  -l "%python(justniffer.simpletest)" -N

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

### **Explanation:**  
- **Handles different connection events**, including opening, requests, responses, and closure.  
- Can be used to **track and analyze network traffic flows**.  
- Allows **custom processing logic** through method overrides.  

This approach is recommended for **advanced traffic monitoring and structured event handling**.  

