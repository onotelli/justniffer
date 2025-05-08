# **Extending Justniffer**  

[HOME](/justniffer) [MAN](MAN)

Justniffer can be extended using **external scripts** in three different ways:  
- **Bash Scripts** – Execute a script at every log entry.  

- **Python Functions** – Process logs with a function called on each entry.  
  
- **Python Handlers** – Implement structured event handling for network traffic advanced analysis (implementing a Python class).  

Each method offers flexibility depending on the level of customization and control required.  

---

## 🔹 **Extending with a Bash Script**  

Justniffer allows the execution of external scripts using the -e option, which is triggered for every log entry. Instead of being printed, the log is passed to the script via stdin, and the script is responsible for processing the input and printing the output.

It's called a log entry, not a log line, because a log entry can span multiple lines.

### **Usage Example:**  
Run Justniffer with a Bash script for log processing:  
```bash
sudo justniffer -i any -l '%request' -e ./test.sh
```

### **Example Script (`test.sh`)**  
```bash
#!/bin/bash
# sudo justniffer  -e ./test.sh -l dest.ip:%dest.ip:%dest.port%newline%request  -i any  

while read inputline
do 
    text=`echo "$inputline" | grep -i -E  host\|dest\.ip`
    if [ "$text" != "" ]; then
        echo $text;
    fi;
done
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

```bash
sudo justniffer  -P simple-example.py  -i any  \
-l "%source.ip:%source.port %dest.ip:%dest.port%newline%request.header%newline%response.header"
```

```python
import re

HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

def app(log: bytes):
    print('-' * 190)
    is_http = False
    for idx, line in enumerate(log.decode('utf-8', errors='ignore').splitlines()):
        if idx == 0:
            print(line)
        if idx == 1:
            for method in HTTP_METHODS:
                if line.startswith(method):
                    is_http = True
                    break
        if  is_http:
            print(line)
```


This method is useful for basic log manipulation and text processing. It is more optimized than the Bash script example because it does not spawn a new process for each log entry. Instead, it directly calls the function, with the Python module being imported only once.

In the provided example, the function first prints the source IP, source port, destination IP, and destination port. Then, it prints the request headers and response headers, but only for HTTP requests

By default, the function "app" is called. However, if needed, you can specify a different function using the format **-P script.py:other_function**.


---

## 🔹 **Extending with Python Handlers**  

For structured event-driven handling, implement a **Python class** that reacts to different network events.  

### **Interface Definition (`ExchangeBase`)**  

```python
Endpoint = tuple[str, int]
Conn = tuple[Endpoint, Endpoint]

class ExchangeBase:
    # called when a connection's syn packet is sent
    def on_opening(self, conn: Conn, time: float) -> None:
        pass

    # called when the connection is established
    def on_open(self, conn: Conn, time: float) -> None:
        pass

    # called when a request fragment is received, applying to every tcp packet 
    # which has already been defragmented, ordered, and deduplicated
    def on_request(self, conn: Conn, content: bytes, time: float) -> None:
        pass

    # called when a response fragment is received, applying to every tcp packet 
    # which has already been defragmented, ordered, and deduplicated
    def on_response(self, conn: Conn, content: bytes, time: float) -> None:
        pass

    # called when the connection is closed, if triggered before on_open
    # it means the connection was refused or filtered
    def on_close(self, conn: Conn, time: float, source_ip: str, source_port: int) -> None:
        pass

    # called when the sniffer is interrupted in the middle of a connection
    def on_interrupted(self) -> None:
        pass

    # called when the connection times out
    def on_timed_out(self, conn: Conn, time: float) -> None:
        pass

    # called to get the result to be logged, if none is returned no log will be generated
    def result(self, time: float) -> str | None:
        pass
```

The `result` method is typically called after a request/response transaction has completed.
It serves as the final step in processing, allowing the system to log or return a result based on the interaction.

### Object Life Cycle:
Here's a general flow of the object's lifecycle based on your sequence:

-  **Created** – The object is instantiated.
- **on_opening** – A SYN packet is sent, indicating the start of a connection attempt.
- **on_open** – The connection is successfully established.
- **on_request** – A request fragment is received, meaning data from the client has been processed.
- **on_response** – A response fragment is received, meaning data from the server has been processed.
- **on_close or on_interrupted or on_timed_out** – The connection is closed, interrupted, or times out.
- **result** – The transaction is complete, and this method is called to retrieve the final outcome for logging or further processing.
- **Deleted** – The object is removed, either manually or by garbage collection when it's no longer needed.

This lifecycle ensures a structured sequence of events where each interaction is captured at the right stage.



### **Usage Example:**  
    sudo PYTHONPATH=. justniffer -i any  -l "%python(simpletest)" -N

The -N option prevents an automatic newline from being added at the end of each log entry. The Python handler has full control over whether to log or not.


### **Example Python Handler (`simpletest.py`)**
```python


METHODS = [m.encode() for m in ('GET', 'POST', 'PUT', 'PATCH', 
                                'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT')]

class Exchange:
    _response: bytes| None
    def __init__(self) -> None:
        self._request = b''
        self._response = None

    def on_request(self, conn, content: bytes, time: float) -> None:
        self._request+=content

    def on_response(self, conn, content: bytes, time: float) -> None:
        if self._response is None: 
            self._response = content 

    def result(self, time:float) -> str | None:
        for m in METHODS:
            if self._request.startswith(m):
                line = self._request.decode(errors='ignore').split('\r')[0]
                if self._response is not None:
                    line += ' | ' + (str(self._response.decode(errors='ignore').splitlines()[0]))
                print(line)
        return None
    

app = Exchange
```


This example will log the first line of the request and the first line of the response, but only if the protocol is HTTP


- Handles different connection events:  **opening**, **request**, **response**, and **closing**  

- Can be used to **track and analyze network traffic flows**.  

- Allows **custom processing logic** through method overrides.  

<br/>
This approach is suited for **advanced traffic monitoring and structured event handling**.  



