import socket
import threading
from datetime import datetime
import sys

# Function to scan a single port
def scan_port(host, port, results):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Wait 1 second for connection
        
        # Try to connect to the port
        result = sock.connect_ex((host, port))
        
        # If result is 0, port is open
        if result == 0:
            try:
                # Try to get service name
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            
            result_text = f"Port {port}: OPEN ({service})"
            print(result_text)
            results.append(result_text)
        else:
            print(f"Port {port}: CLOSED")
            
        sock.close()
        
    except socket.timeout:
        print(f"Port {port}: TIMEOUT")
        results.append(f"Port {port}: TIMEOUT")
    except Exception as e:
        print(f"Port {port}: ERROR - {e}")
        results.append(f"Port {port}: ERROR - {e}")

# Main scanner function
def port_scanner(host, start_port, end_port):
    print(f"\n{'='*50}")
    print(f"Scanning host: {host}")
    print(f"Time started: {datetime.now()}")
    print(f"{'='*50}\n")
    
    # Resolve hostname to IP
    try:
        target_ip = socket.gethostbyname(host)
        print(f"Target IP: {target_ip}\n")
    except socket.gaierror:
        print("Hostname could not be resolved. Exiting.")
        return
    
    results = []
    threads = []
    
    # Create a thread for each port (concurrency requirement)
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=scan_port, args=(host, port, results))
        threads.append(thread)
        thread.start()
        
        # Limit to 50 concurrent threads to avoid overwhelming system
        if len(threads) >= 50:
            for t in threads:
                t.join()
            threads = []
    
    # Wait for remaining threads
    for t in threads:
        t.join()
    
    # Log results to file
    log_filename = f"scan_{host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_filename, 'w') as f:
        f.write(f"Port Scan Results for {host} ({target_ip})\n")
        f.write(f"Time: {datetime.now()}\n")
        f.write(f"Ports scanned: {start_port}-{end_port}\n")
        f.write(f"{'='*50}\n\n")
        
        open_ports = [r for r in results if "OPEN" in r]
        if open_ports:
            f.write("OPEN PORTS:\n")
            for result in open_ports:
                f.write(f"  {result}\n")
        else:
            f.write("No open ports found.\n")
    
    print(f"\n{'='*50}")
    print(f"Scan completed! Results saved to: {log_filename}")
    print(f"Open ports found: {len([r for r in results if 'OPEN' in r])}")

# Main program with options
if __name__ == "__main__":
    print("PORT SCANNER")
    print("1. Scan a single host")
    print("2. Scan a range of ports")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        host = input("Enter host (e.g., google.com or 192.168.1.1): ")
        port_range = input("Enter port range (e.g., 1-1000): ")
        try:
            start_port, end_port = map(int, port_range.split('-'))
            port_scanner(host, start_port, end_port)
        except:
            print("Invalid port range format. Use start-end (e.g., 1-1000)")
    
    elif choice == "2":
        hosts = input("Enter hosts separated by commas: ").split(',')
        port_range = input("Enter port range (e.g., 1-1000): ")
        try:
            start_port, end_port = map(int, port_range.split('-'))
            for host in hosts:
                host = host.strip()
                port_scanner(host, start_port, end_port)
        except:
            print("Invalid input. Please check your entries.")
    
    elif choice == "3":
        print("Goodbye!")
        sys.exit(0)
    
    else:
        print("Invalid choice!")