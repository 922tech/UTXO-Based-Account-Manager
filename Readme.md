# Simple UTXO based Blockchain Exchange

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

## UTXO Flow
- On registration each user is given a key pair: private & public
- User submits signed a set of TxInput with their corresponding output.
- Then TxService verifies the signature with the public key of the UTXOs that the TxInputs reference using `DigitalSigner` (which in turn uses ECDSA algorithm)
- If it is valid then it generates the outputs and spend the referenced UTXOs
- Balance is calculated by summing up the values of UTXOs which user's account public key points to

## Cash Flow
- Each user can buy crypto or sell them.
- Buy: A FiatTransaction is created which further gets verified by the payment gateway. On verification, a spend transaction happens on admin wallet that generates UTXO for the user public key. After that server marks fiat transaction as `spent`   
- Sell: User submits a transaction that uses admin public key and the server transfers fiat to the user's bank account.
- Balance is calculated by summing up the values of unspent verified fiat transactions 
