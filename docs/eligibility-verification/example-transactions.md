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

> This JWT was issued at 2021/09/29 05:30:16 (UTC); the subject (Garcia) is 66 years old.

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

### 2. Ineligible senior

> This JWT was issued at 2021/09/29 05:30:16 (UTC), meaning the subject (Hernandez) is 60 years old.

**Request JWT payload**

```json
{
  "jti": "b2bb29dc-6f6a-44a2-83cf-e298123bbbd2",
  "iss": "https://calitp.org",
  "iat": 1632893416,
  "agency": "ABC Transit Company",
  "eligibility": [
    "senior"
  ],
  "sub": "B2345678",
  "name": "Hernandez"
}
```

**HTTP Request**

The preceding header and payload result in the (signed, Base64url-encoded) JWT used in the following `Authorization` header:

```http
GET /api/eligibility HTTP/1.1
Host: verify.gov
Authorization: Bearer eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.ey
JqdGkiOiJiMmJiMjlkYy02ZjZhLTQ0YTItODNjZi1lMjk4MTIzYmJiZDIiLCJpc3MiOiJodHRwczovL2
NhbGl0cC5vcmciLCJpYXQiOjE2MzI4OTM0MTYsImFnZW5jeSI6IkFCQyBUcmFuc2l0IENvbXBhbnkiLC
JlbGlnaWJpbGl0eSI6WyJzZW5pb3IiXSwic3ViIjoiQjIzNDU2NzgiLCJuYW1lIjoiSGVybmFuZGV6In
0.iY58E7ZYQziQ8ZH7iGSwPGp9S1xbFm6JLXFK0D2E-0w
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 243

eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.eyJqdGkiOiJiMmJiMjlkYy02
ZjZhLTQ0YTItODNjZi1lMjk4MTIzYmJiZDIiLCJpc3MiOiJodHRwczovL3ZlcmlmeS5nb3YiLCJpYXQi
OjE2MzI4OTM0MTcsImVsaWdpYmlsaXR5IjpbXX0._hE8UJPYSmQ0q6xymx8UIVF8BrlZry-G82g9ssyP
dO4
```

**Response JWT payload**

Base64url-decoding the JWT in the response body yields the following payload:

```json
{
  "jti": "b2bb29dc-6f6a-44a2-83cf-e298123bbbd2",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "eligibility": []
}
```

The absence of a value in the `eligibility` array indicates that the Request subject associated with this JWT (Hernandez) has
not been verified for any eligibility.

### 3. No eligibility data

> No data on the subject (Smith) exists in the Server's database.

**Request JWT payload**

```json
{
  "jti": "ef8e9805-bb1b-4f97-903b-6b9ab830d604",
  "iss": "https://calitp.org",
  "iat": 1632893416,
  "agency": "ABC Transit Company",
  "eligibility": [
    "senior"
  ],
  "sub": "C3456789",
  "name": "Smith"
}
```

**HTTP Request**

The preceding header and payload result in the (signed, Base64url-encoded) JWT used in the following `Authorization` header:

```http
GET /api/eligibility HTTP/1.1
Host: verify.gov
Authorization: Bearer eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.ey
JqdGkiOiJlZjhlOTgwNS1iYjFiLTRmOTctOTAzYi02YjlhYjgzMGQ2MDQiLCJpc3MiOiJodHRwczovL2
NhbGl0cC5vcmciLCJpYXQiOjE2MzI4OTM0MTYsImFnZW5jeSI6IkFCQyBUcmFuc2l0IENvbXBhbnkiLC
JlbGlnaWJpbGl0eSI6WyJzZW5pb3IiXSwic3ViIjoiQzM0NTY3ODkiLCJuYW1lIjoiU21pdGgifQ.0xp
eyL3GRAQGrGfvreruTra7dbJpjQQ0zLiIqm4H7sE
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 246

eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.eyJqdGkiOiJlZjhlOTgwNS1i
YjFiLTRmOTctOTAzYi02YjlhYjgzMGQ2MDQiLCJpc3MiOiJodHRwczovL3ZlcmlmeS5nb3YiLCJpYXQi
OjE2MzI4OTM0MTcsImVsaWdpYmlsaXR5IjpbXX0.LEITzkSGL4Y7uA30pRYxNG7XjDI0lSYtev5X7hNK
Gn4
```

**Response JWT payload**

Base64url-decoding the JWT in the response body yields the following payload:

```json
{
  "jti": "ef8e9805-bb1b-4f97-903b-6b9ab830d604",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "eligibility": []
}
```

The absence of a value in the `eligibility` array indicates that the Request subject associated with this JWT (Smith) has not
been verified for any eligibility.

**Note** it is important to return an empty `eligibility` array rather than an error message or 4xx HTTP code here.
This way there is no distinction between "exists in the database" and "does not exist in the database".

### 4. Missing request data

> The request lacks a `sub` property, which is required.

**Request JWT payload**

```json
{
  "jti": "b692fa7c-3dca-4d0d-90ba-e5415af48285",
  "iss": "https://calitp.org",
  "iat": 1632893416,
  "agency": "ABC Transit Company",
  "eligibility": [
    "senior"
  ],
  "name": "Garcia"
}
```

**HTTP Request**

The preceding header and payload result in the (signed, Base64url-encoded) JWT used in the following `Authorization` header:

```http
GET /api/eligibility HTTP/1.1
Host: verify.gov
Authorization: Bearer eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.ey
JqdGkiOiJiNjkyZmE3Yy0zZGNhLTRkMGQtOTBiYS1lNTQxNWFmNDgyODUiLCJpc3MiOiJodHRwczovL2
NhbGl0cC5vcmciLCJpYXQiOjE2MzI4OTM0MTYsImFnZW5jeSI6IkFCQyBUcmFuc2l0IENvbXBhbnkiLC
JlbGlnaWJpbGl0eSI6WyJzZW5pb3IiXSwibmFtZSI6IkdhcmNpYSJ9.EtnDvEHY1CjldnH-98dIMwdir
pxbNbuCg18R7uR8Gag
```

**HTTP Response**

```http
HTTP/1.1 400 Bad Request
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 258

eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.eyJqdGkiOiJiNjkyZmE3Yy0z
ZGNhLTRkMGQtOTBiYS1lNTQxNWFmNDgyODUiLCJpc3MiOiJodHRwczovL3ZlcmlmeS5nb3YiLCJpYXQi
OjE2MzI4OTM0MTcsImVycm9yIjp7InN1YiI6Im1pc3NpbmcifX0.1Z53Z2PInyTSQRomcWhcC2Z3c_qL
WoISH7eFv-_JJnE
```

**Response JWT payload**

Base64url-decoding the JWT in the response body yields the following payload:

```json
{
  "jti": "b692fa7c-3dca-4d0d-90ba-e5415af48285",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "error": {
    "sub": "missing"
  }
}
```

The `error` message indicates that the Request subject associated with this JWT is missing.

### 5. Invalid request data

> The request's `sub` property is not in the correct format.

**Request JWT payload**

```json
{
  "jti": "d0dbacaf-e691-4ecc-a733-a42a904da607",
  "iss": "https://calitp.org",
  "iat": 1632893416,
  "agency": "ABC Transit Company",
  "eligibility": [
    "senior"
  ],
  "sub": "12345678Z",
  "name": "Garcia"
}
```

**HTTP Request**

The preceding header and payload result in the (signed, Base64url-encoded) JWT used in the following `Authorization` header:

```http
GET /api/eligibility HTTP/1.1
Host: verify.gov
Authorization: Bearer eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.ey
JqdGkiOiJkMGRiYWNhZi1lNjkxLTRlY2MtYTczMy1hNDJhOTA0ZGE2MDciLCJpc3MiOiJodHRwczovL2
NhbGl0cC5vcmciLCJpYXQiOjE2MzI4OTM0MTYsImFnZW5jeSI6IkFCQyBUcmFuc2l0IENvbXBhbnkiLC
JlbGlnaWJpbGl0eSI6WyJzZW5pb3IiXSwic3ViIjoiMTIzNDU2NzhaIiwibmFtZSI6IkdhcmNpYSJ9.2
w5JhbfIzOSdKWTOrP5CQdhWw9Vo8VunoASe4EVZOoI
```

**HTTP Response**

```http
HTTP/1.1 400 Bad Request
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 258

eyJhbGciOiJIUzI1NiIsImVuYyI6IlJTMjU2IiwidHlwIjoiSldUIn0.eyJqdGkiOiJkMGRiYWNhZi1l
NjkxLTRlY2MtYTczMy1hNDJhOTA0ZGE2MDciLCJpc3MiOiJodHRwczovL3ZlcmlmeS5nb3YiLCJpYXQi
OjE2MzI4OTM0MTcsImVycm9yIjp7InN1YiI6ImludmFsaWQifX0.V_8VA7vWTzwibGE4mfyQ0zAwKhLV
qKDYsl2M55z8rDc
```

**Response JWT payload**

Base64url-decoding the JWT in the response body yields the following payload:

```json
{
  "jti": "d0dbacaf-e691-4ecc-a733-a42a904da607",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "error": {
    "sub": "invalid"
  }
}
```

The `error` message indicates that the Request subject associated with this JWT was invalid.

[hs256]: https://en.wikipedia.org/wiki/SHA-2
[jwtio]: https://jwt.io/
