# Pesaway Simulator

Pesaway Simulator is a small payment API built with Python and Django. It stores payments in a database, but no real money moves. Clients can create payments, list them (optionally filtered by status), view one payment, and update its amount or currency using JSON requests.

Every payment has a unique `reference`. If the same reference is sent twice, the second request is rejected and only one payment is stored.
