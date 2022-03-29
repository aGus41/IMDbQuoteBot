# @IMDbQuoteBot

https://twitter.com/IMDbQuoteBot

Scheduled with crontab:
```

*/3 * * * * python3 reply_to_tweets.py
# Checks its mentions every 3 minutes

15 15 * * Sun,Thu python3 get_random_quote.py
# Writes a random movie quote at 15:15 every Sunday and Thursday

```
# Commit check

