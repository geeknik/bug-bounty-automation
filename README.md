## WIP Bug Bounty Automation

**To start the server:**

Edit the last line of the script to change the port, IP to bind to, and if you want DEBUG enabled. Then run `python3 server.py` from the directory where you want the sqlite3 database to be stored. This directory will also be where the `results/` are stored.

**To initiate a scan:**

`curl -H "Content-Type: application/json" -X POST "http://127.0.0.1:5002" --data '{"domain": "example.com"}'`

**To view results:**

`curl "http://127.0.0.1:5002/results/example.com" | jq .`
