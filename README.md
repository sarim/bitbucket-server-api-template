Bitbucket Server (stash) API Auth Example
==

This flask app demonstrates how to connect to a self-hosted Bitbucket Server (formally known as stash) using OAuth (1.0) and do simple REST calls.

You must create a `.env` file. look to the example file.

You have to set an an application link (incoming) in bitbucket server first, you can skip most fields, but `CONSUMER_KEY` and `RSA_KEY` must match in client and server. You have to generate a RSA key pair. RSA private key must be provided here and public key must be inserted in bitbucket server.