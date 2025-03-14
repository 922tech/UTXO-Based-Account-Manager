# Simple UTXO based Blockchain

## V1
- In this version there is no transaction fee and block logic.
- Only includes account, transaction and the sequence logic

The core logic is implemented at `TxService` class inspiring UTXO-based blockchain systems like Bitcoin.
```
TxOutput >- Transaction -<  TxInput
```
- Each Transaction can have multiple inputs and outputs.
- Every TxInput is checked to be signed by the user's private key

