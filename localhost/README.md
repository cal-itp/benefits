# Benefits: `localhost`

Code and artifacts for testing and running the Benefits application in a local, non-production environment.

## [`data/`](./data)

* `client.json`: sample configuration for the Benefits client
* `server.json`: sample configuration for a local Eligibility Verification server

## [`keys/`](./keys)

* `client.key` and `client.pub`: encryption keypair for the Benefits client
* `server.key` and `server.pub`: encryption keypair for the local Eligibility Verification server

## [`server/`](./server)

* Simple Flask app implementing Eligiblity Verification server

## [`Dockerfile.dev`](./Dockerfile.dev)

* Docker image built on the [Benefits Docker image](../Dockerfile) used with
[VS Code devcontainers](https://code.visualstudio.com/docs/remote/containers).
