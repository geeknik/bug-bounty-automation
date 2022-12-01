## WIP Bug Bounty Automation

**To initiate a scan:**

`curl -H "Content-Type: application/json" -X POST "http://127.0.0.1:5002" --data '{"domain": "example.com"}'`

**To view results:**

`curl "http://127.0.0.1:5002/results/example.com" | jq .`
