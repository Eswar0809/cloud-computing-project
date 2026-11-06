# Subnetting and Network Access Control (Task 5)

## 1. Subnet Allocation Working

We are assigned the IPv4 address block `10.20.0.0/16`.
The block has $2^{32-16} = 2^{16} = 65,536$ total IP addresses spanning `10.20.0.0` to `10.20.255.255`.

As per requirements, subnets are allocated in descending order of required host count (largest requirement to smallest), starting at `10.20.0.0`, placing each subnet immediately after the previous one, using the smallest prefix that satisfies each host requirement. Usable hosts are calculated as $2^{(32 - \text{prefix})} - 2$ (excluding the network address and broadcast address).

### Subnet 1: `app` Subnet
- **Hosts Needed**: 1,000
- **Prefix Calculation**:
  - $2^9 - 2 = 510$ (too small)
  - $2^{10} - 2 = 1,022 \ge 1,000$ (fits requirement)
  - Host bits: $h = 10 \implies \text{Prefix} = 32 - 10 = /22$
  - Block size: $2^{10} = 1,024$ addresses ($4 \times /24$ blocks)
- **Base Address**: `10.20.0.0`
- **Network Address**: `10.20.0.0/22`
- **Usable Host Range**: `10.20.0.1` to `10.20.3.254`
- **Broadcast Address**: `10.20.3.255`
- **Usable Hosts**: $1,022$
- **Next Available Address**: `10.20.4.0`

### Subnet 2: `public` Subnet
- **Hosts Needed**: 250
- **Prefix Calculation**:
  - $2^7 - 2 = 126$ (too small)
  - $2^8 - 2 = 254 \ge 250$ (fits requirement)
  - Host bits: $h = 8 \implies \text{Prefix} = 32 - 8 = /24$
  - Block size: $2^8 = 256$ addresses
- **Base Address**: `10.20.4.0`
- **Network Address**: `10.20.4.0/24`
- **Usable Host Range**: `10.20.4.1` to `10.20.4.254`
- **Broadcast Address**: `10.20.4.255`
- **Usable Hosts**: $254$
- **Next Available Address**: `10.20.5.0`

### Subnet 3: `data` Subnet
- **Hosts Needed**: 100
- **Prefix Calculation**:
  - $2^6 - 2 = 62$ (too small)
  - $2^7 - 2 = 126 \ge 100$ (fits requirement)
  - Host bits: $h = 7 \implies \text{Prefix} = 32 - 7 = /25$
  - Block size: $2^7 = 128$ addresses
- **Base Address**: `10.20.5.0`
- **Network Address**: `10.20.5.0/25`
- **Usable Host Range**: `10.20.5.1` to `10.20.5.126`
- **Broadcast Address**: `10.20.5.127`
- **Usable Hosts**: $126$
- **Next Available Address**: `10.20.5.128`

### Subnet 4: `management` Subnet
- **Hosts Needed**: 20
- **Prefix Calculation**:
  - $2^4 - 2 = 14$ (too small)
  - $2^5 - 2 = 30 \ge 20$ (fits requirement)
  - Host bits: $h = 5 \implies \text{Prefix} = 32 - 5 = /27$
  - Block size: $2^5 = 32$ addresses
- **Base Address**: `10.20.5.128`
- **Network Address**: `10.20.5.128/27`
- **Usable Host Range**: `10.20.5.129` to `10.20.5.158`
- **Broadcast Address**: `10.20.5.159`
- **Usable Hosts**: $30$
- **Next Available Address**: `10.20.5.160`

---

## 2. Subnet Allocation Table

| Subnet | Network Address | Prefix Length | Usable Host Range | Broadcast Address | Number of Usable Hosts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **app** | `10.20.0.0` | `/22` | `10.20.0.1` – `10.20.3.254` | `10.20.3.255` | 1,022 |
| **public** | `10.20.4.0` | `/24` | `10.20.4.1` – `10.20.4.254` | `10.20.4.255` | 254 |
| **data** | `10.20.5.0` | `/25` | `10.20.5.1` – `10.20.5.126` | `10.20.5.127` | 126 |
| **management** | `10.20.5.128` | `/27` | `10.20.5.129` – `10.20.5.158` | `10.20.5.159` | 30 |

---

## 3. Stateless NACL Reasoning & Rule Ordering Analysis

### A. Why a Stateless NACL Requires Explicit Rules for Reply Traffic
A network access control list (NACL) is inherently **stateless**. Unlike stateful inspection engines (e.g., Security Groups) that maintain an internal connection state table to correlate incoming TCP ACK packets with initiated TCP SYN sessions, a stateless NACL inspects each IP packet in strict isolation without tracking connection lifecycle.

Consequently, bidirectional communication requires two independent, explicit rule permissions:
1. **Client-to-Public Ingress & Egress**: When an external client initiates an HTTPS connection from an ephemeral port (e.g., port 54321) to port 443 on the public load balancer, the inbound rule allows port 443. However, when the load balancer replies, the packet travels **outbound** towards destination port 54321 on the client. Without an outbound rule explicitly permitting traffic to destination ephemeral ports (`1024–65535`), the server's reply is dropped by the default deny rule.
2. **Public-to-App Ingress & Egress**: Similarly, when the public load balancer forwards traffic to backend containers in the `app` subnet on TCP port 8000, outbound rule 100 permits destination port 8000. When the backend app responds, its reply packet enters the public subnet with a destination port matching the load balancer's client-side ephemeral port (`1024–65535`). Without inbound rule 400 permitting traffic from `10.20.0.0/22` to ports `1024–65535`, backend responses would be dropped.

### B. Why Rule Ordering Matters for `198.51.100.0/24`
NACL rules are processed sequentially in **strictly ascending numerical order** (lowest rule number first). When a packet matches a rule's criteria, the specified action (`allow` or `deny`) is applied immediately and evaluation terminates (**first-match semantics**).

Because `198.51.100.0/24` is a subnet of `0.0.0.0/0`, ordering is critical:
- Placing the **DENY** rule at **Rule 100** ensures that any packet originating from the abusive range `198.51.100.0/24` is inspected and dropped before broader rules are considered.
- If the allow rules (Rule 200 for port 80, Rule 210 for port 443 with CIDR `0.0.0.0/0`) were numbered lower than Rule 100 (e.g., Rule 50), an abusive packet from `198.51.100.9` targeting port 443 would match Rule 50 first and be granted entry. The deny rule at Rule 100 would never be evaluated, completely subverting the security policy.
