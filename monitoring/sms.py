import os
import messagebird

client = messagebird.Client(os.environ["MESSAGEBIRD_KEY"])
message = client.message_create(
    "+31629513980", "+31629513980", "Laatste bericht"
)
