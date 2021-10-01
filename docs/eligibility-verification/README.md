# API Specification

This document outlines the requirements for data exchange to verify one or more eligibility criteria for transit benefits.

## Security

### Actors

* The **API Client** communicates with an API Server on behalf of a user. The Client makes [Requests](#request).
* An **API Server** holds information enabling fulfillment of an eligibility verification transaction. The Server sends
  [Responses](#response)

Under these definitions, the [`benefits`](../README.md) application acts as the Client and communicates with partner Servers.

For the purposes of testing and development, the `benefits` code repository includes an example Server, which can be run
locally. Read more about the [Test eligibility server](../getting-started/test-eligibility-server.md).

### Authentication/Authorization

The Server must be secured and allow only authorized Clients to make requests. API requests are secured via
client secrets sent with the HTTP headers.

### Transport

All API requests and responses must be made over an encrypted HTTPS connection utilizing [TLS][tls] 1.2 or higher.

This API uses a data interchange format known as [JSON Web Token][jwt] (JWT); JWT is an [open industry standard][jwt-standard]
method of representing claims securely between two parties. Built into JWT are important protections for data integrity and
data source verification.

### Message signing

JWT is designed to use a digital signature, allowing the Server to verify that data received was not modified by a third-party
after being sent by the Client. Request and response payloads must be signed with public-key cryptography, which allows the
recipient to validate that the payload came from a known sender.

Signing algorithms supporting public-key cryptography include the RSA family (e.g. RSA-256) and ECDSA.

### Message encryption

The Request JWT must be encrypted by the Client before sending, using a public key published by the Server. The Server's
Response JWT must also be encrypted, using a public key published by the Client.

### Composing a message

Based on [*connect2id Nested signed and encrypted JSON Web Token (JWT)*][connect2id].

1. Build JWT header and (request/response) payload (See [API documentation](#api-documentation))
1. Generate signature for JWT using the sender’s private key
1. Put header, claims, and signature together into a Signed JWT (JWS)
1. Encrypt JWS using the recipient’s public key (JWE)
1. [Base64url-encode][b64e] JWE
1. JWE is sent with (request/response)

## API Documentation

Below is a description of the HTTP request and response, and request and response payloads. The payloads each make use of
[JWT Registered claims][jwt-registered] as well as [Private claims][jwt-private].

**All fields are required.** Fields names marked with ***** are Registered claims defined by the JWT specification.

Complete example transactions can be found on [another page](example-transactions.md).

### Header

The same header is shared between Request and Response JWTs.

| Field name | Data type   | Notes                               |
|------------|-------------|-------------------------------------|
| `alg`***** | `string`    | The signature algorithm             |
| `enc`***** | `string`    | The encryption algorithm            |
| `typ`***** | `string`    | The type of token; must equal "JWT" |

**Header example:**

```json
{
  "alg": "RS256",
  "enc": "RS256",
  "typ": "JWT"
}
```

### Request

Requests are sent as HTTP GET requests to the Server:

```http
GET /api/eligibility HTTP/1.1
Host: verify.gov
Authorization: Bearer <JWT>

```

The URL endpoint is defined by the implementing Server. The Request JWT is sent as a Base64url-encoded Bearer token in the
`Authorization` header. There is no Request Body and querystring parameters are undefined.

**Request JWT payload:**

| Field name    | Data type       | Notes                                                                                      |
|---------------|-----------------|--------------------------------------------------------------------------------------------|
| `jti`*****    | [`UUID4`][uuid] | Unique identifier for this JWT                                                             |
| `iss`*****    | `string`        | Identifier for the issuer of the JWT (e.g. the Client)                                     |
| `iat`*****    | `integer`       | The time at which the JWT was issued; expressed as [Unix][unix] seconds                    |
| `agency`      | `string`        | Identifier for the transit agency the JWT was issued on behalf of                          |
| `eligibility` | `string[]`      | An array of [eligibility types][types] to verify                                           |
| `sub`*****    | `string`        | The subject of the JWT, expressed as the transit rider's ID (e.g. Driver's License number) |
| `name`        | `string`        | The transit rider's last name                                                              |

**Request payload example:**

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

### Response

The response body contains the Base64url-encoded Response JWT:

```http
HTTP/1.1 200 OK
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 232

JWT
```

**Response JWT payload:**

The Server response is intentionally sparse, omitting all PII from the original Request.

| Field name    | Data type       | Notes                                                                                |
|---------------|-----------------|--------------------------------------------------------------------------------------|
| `jti`*****    | [`UUID4`][uuid] | The identifier from the Request JWT                                                  |
| `iss`*****    | `string`        | Identifier for the issuer of the JWT (e.g. the Server)                               |
| `iat`*****    | `integer`       | The time at which the JWT was issued; expressed as [Unix][unix] seconds              |
| `eligibility` | `string[]`      | An array of [eligibility types][types] that verify as `TRUE` for the Request         |

**Response payload example:**

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

### Errors

An error can occur if the Request does not contain appropriate data. Errors are returned as JWT payloads in the same way that
regular Responses are returned, with a HTTP code 400.

```http
HTTP/1.1 400 Bad Request
Date: Wed, 29 Sep 2021 05:30:17 GMT
Content-Type: text/plain; charset=UTF-8
Content-Length: 232

JWT
```

**Error JWT payload:**

| Field name    | Data type          | Notes                                                                   |
|---------------|--------------------|-------------------------------------------------------------------------|
| `jti`*****    | [`UUID4`][uuid]    | The identifier from the Request JWT                                     |
| `iss`*****    | `string`           | Identifier for the issuer of the JWT (e.g. the Server)                  |
| `iat`*****    | `integer`          | The time at which the JWT was issued; expressed as [Unix][unix] seconds |
| `error`       | `{string: string}` | A dictionary mapping field name to error message                        |

**Example: missing value**

Occurs when one or more fields are missing (either missing from the payload, or with a null/empty value).

```json
{
  "jti": "0890cce7-25d3-425c-a81b-bc437c2e18a3",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "error": {
    "eligibility": "missing"
  }
}
```

**Example: invalid format**

Occurs when one or more fields contain data that is invalid according to the Server's interpretation.

```json
{
  "jti": "0890cce7-25d3-425c-a81b-bc437c2e18a3",
  "iss": "https://verify.gov",
  "iat": 1632893417,
  "error": {
    "sub": "invalid"
  }
}
```

### Eligibility types

Naturally, the Client and Server must agree on values for the `eligibility` array. Typically the Server's definition(s) and
type(s) will be agreed upon and used by the Client, as the server is responsible for determining eligibility of a given type.

[b64e]: https://en.wikipedia.org/wiki/Base64#The_URL_applications
[connect2id]: https://connect2id.com/products/nimbus-jose-jwt/examples/signed-and-encrypted-jwt
[jwt]: https://jwt.io/introduction/
[jwt-private]: https://tools.ietf.org/html/rfc7519#section-4.3
[jwt-registered]: https://tools.ietf.org/html/rfc7519#section-4.1
[jwt-standard]: https://tools.ietf.org/html/rfc7519
[tls]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[types]: #eligibility-types
[unix]: https://en.wikipedia.org/wiki/Unix_time
[uuid]: https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)
