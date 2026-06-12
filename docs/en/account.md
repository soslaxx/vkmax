# Account management

Destructive operations on the account itself. **All three are
irreversible from the server's point of view** — handle with care.

## Schedule account deletion

MAX implements a delayed deletion: the account is scheduled to be
wiped after `days` days, during which a login cancels it.

```python
await client.set_account_delete_timer(days=7)
await client.set_account_delete_timer(delete_time=1799999999999)  # ms
```

Server returns the resulting `deleteTime`.

Cancel a pending deletion:

```python
await client.cancel_account_delete_timer()
```

## Delete immediately

Opcode 199 (`PROFILE_DELETE`). The exact required payload is not
documented by komet, so this helper sends only what you pass:

```python
await client.delete_account()
await client.delete_account(password="...", track_id="...", reason="...")
```

If the server expects an `auth_track` flow (create track + validate
password), do that first:

```python
track_id = await client.create_auth_track()
await client.validate_password(track_id, "my_2fa_password")
await client.delete_account(password="my_2fa_password", track_id=track_id)
```

## Change phone number

Mobile API uses `PHONE_BIND_REQUEST` (98) + `PHONE_BIND_CONFIRM` (99):

```python
start = await client.request_phone_change("+79991234567")
# server sends SMS to that number; `start['token']` is the bind token
await client.confirm_phone_change(start["token"], input("code: "))
```

The new number replaces the old one on success. Your session token
stays valid.

## Bind / verify email

```python
track_id = await client.create_auth_track()
await client.request_email_verify(track_id, "user@example.com")
# server sends code to email
await client.check_email_code(track_id, input("email code: "))
```

## Logout

```python
await client.logout()                       # current session
await client.logout(push_token="<fcm>")     # also drop push token
```

Logout clears the cached token from disk.
