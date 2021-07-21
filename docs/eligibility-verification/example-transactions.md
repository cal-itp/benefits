# Example transactions

This page outlines example roundtrip HTTP transactions conforming to the [Eligibility Verification API](README.md).

## Sample server

For the following examples, assume a Server with a database like:

| Driver's License Number | Last Name | Date of Birth |
|-------------------------|-----------|---------------|
| A1234567                | Garcia    | 1955-08-27    |
| B2345678                | Hernandez | 1961-01-23    |

Further, assume the Server validates the eligibility type `senior` for those individuals age 65 or older.

## Usage of JWT in examples

For the purposes of these examples, JWT signing will be done using the simpler, secret-based [HMAC SHA-256][hs256] (HS256)
signing algorithm. **This is not appropriate for production** as it does not carry the same guarantees as a public-key signing
algorithm.

## Example JWT header

Although the header will indicate otherwise, for simplification the examples *will not show encryption/decryption* of the JWT.

The JWT header (both Request and Response) for each of the following examples is:

```json
{
  "alg": "HS256",
  "enc": "RS256",
  "typ": "JWT"
}
```

## Test encoding/decoding

To test JWT encoding/decoding, use the Debugger tool on [JWT.IO][jwtio]. Paste in an encoded key to get the decoded output.
Or build decoded output to see the corresponding encoded key.

**This tool must not be used with real (PII) data.**

## Examples

### 1. Eligible senior

> This JWT was issued at 2021/09/29 05:30:16 (UTC); the subject (Garcia) is 65 years old.

**Request JWT payload**

```json
{
  "jti": "0890cce7-25d3-425c-a81b-bc437c2e18a3",
  "iss": "https://calitp.org",
  "iat": 1632893416,
  "agency": "ABC Transit Company",
  "eligibility": [
    "senior"
  ],
  "sub": "A1234567",
  "name": "Garcia"
}
```

**HTTP Request**

The preceding header and payload result in the (signed, Base64url-encoded) JWT used in the following `Authorization` header:

```http
GET /api/eligibility HTTP/1.1
Host: verify.gov
Authorization: Bearer eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.ey
JqdGkiOiIwODkwY2NlNy0yNWQzLTQyNWMtYTgxYi1iYzQzN2MyZTE4YTMiLCJpc3MiOiJodHRwczovL2
NhbGl0cC5vcmciLCJpYXQiOjE2MzI4OTM0MTYsImFnZW5jeSI6IkFCQyBUcmFuc2l0IENvbXBhbnkiLC
JlbGlnaWJpbGl0eSI6WyJzZW5pb3IiXSwic3ViIjoiQTEyMzQ1NjciLCJuYW1lIjoiR2FyY2lhIn0.sM
VsPU4ByJNR9lADrjlZHeNi1NkBoPdXO50fnCFDDqM
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 254

eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.eyJqdGkiOiIwODkwY2NlNy0y
NWQzLTQyNWMtYTgxYi1iYzQzN2MyZTE4YTMiLCJpc3MiOiJodHRwczovL3ZlcmlmeS5nb3YiLCJpYXQi
OjE2MzI4OTM0MTcsImVsaWdpYmlsaXR5IjpbInNlbmlvciJdfQ.tos2vJOO6msv9tMDMT34f95aIRvYj
sHRVUz5621fNlI
```

**Response JWT payload**

Base64url-decoding the JWT in the response body yields the following payload:

```json
{
  "jti": "0890cce7-25d3-425c-a81b-bc437c2e18a3",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "eligibility": [
    "senior"
  ]
}
```

The presence of the value `"senior"` in the `eligibility` array indicates that the Request subject associated with this JWT
(Garcia) has been verified for that eligibility.

[hs256]: https://en.wikipedia.org/wiki/SHA-2
[jwtio]: https://jwt.io/
