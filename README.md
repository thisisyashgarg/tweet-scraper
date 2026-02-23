# Twitter/X Tweet Fetcher

Fetch tweets from any Twitter/X user using the GraphQL API.

## Quick Start

1. **Install dependency**
   ```bash
   pip install aiohttp
   ```

2. **Create your config**
   ```bash
   cp config.example.json config.json
   ```

3. **Fill in your credentials** — open `config.json` and set:

   | Key                  | Where to find it                                                        |
   | -------------------- | ----------------------------------------------------------------------- |
   | `user_id`            | Inspect any tweet from the target user → GraphQL response → `rest_id`  |
   | `auth_token`         | Browser DevTools → Application → Cookies → `auth_token`                |
   | `csrf_token`         | Browser DevTools → Application → Cookies → `ct0`                       |
   | `cookies`            | Copy all cookie key/values from DevTools (see `config.example.json`)    |

4. **Run**
   ```bash
   python fetch_tweets.py              # uses config.json
   python fetch_tweets.py myconf.json  # uses a custom config file
   ```

## Config Reference

| Field                | Type         | Default        | Description                                      |
| -------------------- | ------------ | -------------- | ------------------------------------------------ |
| `user_id`            | `string`     | *(required)*   | Numeric Twitter user ID of the target account     |
| `target_tweet_count` | `int\|null`  | `null`         | Max tweets to fetch; `null` = fetch all           |
| `tweets_per_page`    | `int`        | `20`           | Tweets per API page (max ~20)                     |
| `output_file`        | `string`     | `tweets.json`  | Output JSON file path                            |
| `auth_token`         | `string`     | *(required)*   | Your `auth_token` cookie value                   |
| `csrf_token`         | `string`     | *(required)*   | Your `ct0` / CSRF token                          |
| `cookies`            | `object`     | *(required)*   | All cookies as key-value pairs                   |

## Security

- `config.json` is git-ignored to prevent accidental credential leaks.
- **Never commit your `config.json`** — share only `config.example.json`.
