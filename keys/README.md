# keys

*These keys are just samples*. They cannot be used for production systems.

Generate a new keypair and exchange public keys with the Eligibility Verification Server.

## Generate a new keypair

Using a terminal and `openssl`:

```bash
openssl genrsa -out [file name].key 2048
```

Then extract the public key:

```bash
openssl rsa -in [private key created above].key -pubout > [file name].pub
```

There are two new files:

* `[file name].key`: private key in PEM format, apply to a `TransitAgency` instance in Django
* `[file name].pub`: public key in PEM format, give to the Eligibility Verification server

A public key in PEM format from the Eligibility Verification server is also required, and must be applied to an
`EligiblityVerifier` instance in Django.

To get a single-line version suitable for a JSON file:

```bash
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' [key file].ext
```
