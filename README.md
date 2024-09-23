---

# **SpeedyCHAIN and STORDY Installation and Execution Guide (Linux)**

![SpeedyCHAIN Logo](API/pages/assets/images/speedychain-logo.svg)

**SpeedyCHAIN** is a blockchain prototype designed to run on IoT devices. It integrates with **STORDY**, a storage module, and also includes an optional **Ethereum Virtual Machine (EVM)** integration for testing purposes. This guide provides step-by-step instructions on installing and running SpeedyCHAIN, STORDY, and the EVM.

---

## **1. Update the Linux Environment**

Before proceeding, ensure your system is up to date:

```bash
sudo apt update
sudo apt upgrade
```

---

## **2. Install Git**

Git is required for cloning the necessary repositories. Install it with:

```bash
sudo apt install git
```

---

## **3. Install Python 2 and Pip2**

### **3.1 Install Python 2**

```bash
sudo apt install python2
```

Verify the installation:

```bash
python2 --version
```

### **3.2 Install Pip2**

1. Download the Pip installation script for Python 2:

   ```bash
   curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
   ```

2. Run the script to install Pip2:

   ```bash
   sudo python2 get-pip.py
   ```

3. Verify the installation:

   ```bash
   pip2 --version
   ```

---

## **4. Install Python 3 and Pip3**

Install Python 3 and Pip3:

```bash
sudo apt install python3-pip
```

Verify the installation:

```bash
pip3 --version
```

---

## **5. Clone the SpeedyCHAIN and STORDY Repositories**

### **5.1 Clone SpeedyCHAIN**

Clone the SpeedyCHAIN repository:

```bash
git clone https://github.com/conseg/speedychain.git
```

### **5.2 Clone STORDY**

Clone the STORDY storage module:

```bash
git clone https://github.com/leonardocreatus/stordy.git
```

---

## **6. Install Required Dependencies**

### **6.1 Python 3 Dependencies**

Install the required dependency for Python 3:

```bash
pip3 install Pyro4
```

### **6.2 Python 2 Dependencies**

Install the necessary Python 2 packages:

```bash
pip2 install Pyro4
pip2 install Flask
pip2 install merkle
pip2 install pycryptodome
pip2 install requests
```

---

## **7. Running STORDY**

### **7.1 Navigate to the STORDY Directory**

Navigate to the **STORDY** directory:

```bash
cd stordy
```

### **7.2 Install Cargo**

Install Cargo on your system:

```bash
sudo apt install cargo
```

### **7.3 Install protobuf-compiler**

Install protobuf-compiler:

```bash
sudo apt-get install protobuf-compiler
```

### **7.4 Run STORDY**

Run the STORDY storage module using Cargo (make sure you have Rust installed):

```bash
cargo run
```

---

## **8. Running SpeedyCHAIN with the STORDY Module**

### **8.1 Switch to the Correct Branch**

Navigate to the **SpeedyCHAIN** repository and switch to the `stordy-module` branch:

```bash
cd ../speedychain
git checkout stordy-module
```

### **8.2 Navigate to the API Directory**

Go to the API directory inside the **SpeedyCHAIN** project:

```bash
cd API
```

---

## **9. Running SpeedyCHAIN**

### **9.1 Start the Network Node**

Start a Pyro4 naming service (a network node) using Python 3:

```bash
python3 -m Pyro4.naming -n 127.0.0.1 -p 9090
```

### **9.2 Start the Gateways**

Start two gateways using Python 2:

1. Start Gateway A:

   ```bash
   python2 runner.py -n 127.0.0.1 -p 9090 -G gwa -C 0001 -S 1
   ```

2. Start Gateway B:

   ```bash
   python2 runner.py -n 127.0.0.1 -p 9090 -G gwb -C 0001 -S 1
   ```

---

## **10. Optional: Ethereum Virtual Machine (EVM) Integration**

The **Ethereum Virtual Machine (EVM)**, written in Go, can be used for testing. Here's how to set it up:

### **10.1 Install Golang**

Follow the official Go installation guide: [Golang Install Instructions](https://golang.org/doc/install)

### **10.2 Compile the EVM**

After installing Go, use the following commands to set up the EVM:

1. Fetch the Go Ethereum package:

   ```bash
   go get github.com/ethereum/go-ethereum
   ```

2. Navigate to the EVM folder:

   ```bash
   cd go-ethereum
   ```

3. Build the EVM:

   ```bash
   go build
   ```

### **10.3 Quickstart**

To quickly start the EVM, follow the steps below:

1. Run the `quickstart.sh` script:

   ```bash
   ./quickstart.sh
   ```

2. If the EVM is needed for testing, uncomment the EVM-related line in the `quickstart.sh` script and re-run it.

---

## **11. Running the P2P Script**

The **P2P.py** script manages the peer-to-peer network within SpeedyCHAIN.

### **How to Run P2P.py:**

1. Adjust the IP in the `P2P.py` file to match your setup.
2. Run the script using Python 3:

   ```bash
   sudo python3 P2P.py
   ```

   (Note: An `[Errno 98]` error is normal and expected.)

3. Execute the `sendRequest.sh` script:

   ```bash
   sudo ./sendRequest.sh
   ```

4. Follow the script prompts:
   - Option 5: Insert the IP.
   - Option 7: Select it.
   - Option 1: Initiate the connection.
   - Option 2: Send the request.
   - Option 8: List information.

5. Repeat steps 6 and 7 as necessary.

---

## **12. TODO List for Further Improvements**

- Implement a consensus algorithm.
- Improve REST methods.
- Auto-generate keys (for testing purposes).
- Instrumentalize code and parameterize time collection.
- Modify the genesis block hash to point to the block header hash.

---

## **13. Additional Resources**

- **Key folder**: This folder contains a set of public and private keys generated for testing purposes.
- **CORE Emulator Tutorial**: [Setting up CORE emulator infrastructure](https://www.youtube.com/watch?v=xCGu3r73xl4)
- **SpeedyCHAIN & DeviceSimulator (Deprecated)**: [Setup tutorial](https://www.youtube.com/watch?v=3MA8HBgbA8k)

---

## **Final Considerations**

- **Node**: Represents a point in the SpeedyCHAIN network that communicates with other nodes.
- **Gateway**: Entry points that connect and transmit data between nodes.
- **STORDY**: Storage module integrated with SpeedyCHAIN for handling data persistence.
- **EVM**: Optional Ethereum Virtual Machine integration for testing smart contracts.

By now, both **SpeedyCHAIN** and **STORDY** should be set up and running on your Linux environment. If you encounter any issues, review the steps carefully and ensure that all dependencies are installed correctly.

---
