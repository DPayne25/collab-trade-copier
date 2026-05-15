# Trade Copier
A *multi-account execution engine* for Forex trading. The core objective of this system is to automate exact position duplication across an account matrix from a single execution source.

# Operational Model
- **Master Trigger:** The user executes a trade manually or algorithmically on a designated Master account.
- **Configuration Mapping:** The engine reads the target infrastructure and account profiles defined in the local configuration file.
- **Simultaneous Distribution:** The engine broadcasts the trade parameters to all configured target accounts concurrently. 
  - **Fixed Parameters:** Entry price levels, stop losses, and take profit targets are mirrored identically across all endpoints.
  - **Variable Parameters (Dynamic Sizing):** The volume (lot size) is calculated independently for each target account based on configuration file rules, allowing for fixed-lot allocations or dynamic percentage-based risk scaling tailored to individual account balances.

# Instructions to Test

Run the following: 

## Linux

```bash
wsl

python3 -m pip install .venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```
