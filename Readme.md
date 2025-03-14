# Simple UTXO based Blockchain

## V1
- In this version there is no transaction fee and block logic.
- Only includes account, transaction and the sequence logic
- The core logic is implemented in `apps.blockchain.services` which encapsulates the service layer of the system 
- The blockchain logic is implemented at `apps.blockchain.services.TxService` inspiring UTXO-based blockchain systems like Bitcoin.
Models:
```
TxOutput >- Transaction -<  TxInput
Account >- FiatTransaction -< Transaction
```
- Each Transaction can have multiple inputs and outputs.
- Every TxInput is checked to be signed by the user's private key
- Every FiatTransaction references one Transaction and one Account.

