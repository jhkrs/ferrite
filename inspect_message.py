from eth_account.messages import encode_defunct

# Create a signable message
message = encode_defunct(text="inspect me")

print("--- Inspecting SignableMessage object ---")

print("\n--- dir(message) ---")
print(dir(message))

print("\n--- vars(message) ---")
try:
    print(vars(message))
except TypeError as e:
    print(f"Could not call vars() on the object: {e}")

print("\n--- Inspecting attributes individually ---")
for attr in dir(message):
    if not attr.startswith('__'):
        try:
            value = getattr(message, attr)
            print(f"  - message.{attr}: {value}")
        except Exception as e:
            print(f"  - Could not get attribute {attr}: {e}")

print("\n--- End of inspection ---")
