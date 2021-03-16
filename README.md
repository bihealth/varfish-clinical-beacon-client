# Clinical Beacon API Client

Except for authentication uses official GA4GH Beacon protocol.

- https://github.com/ga4gh-beacon/specification

To facilitate controlled access without the burden of implementing OAuth, the upcoming IETF standard "Signing HTTP Messages" is employed:

- https://tools.ietf.org/html/draft-ietf-httpbis-message-signatures-01

The assumption is that two trusted sites are connected and both the querying and the responding site trust each other.

Briefly, you have to specify:

- `X-Beacon-User` HTTP header
- `Authorization` HTTP header with `Signature` as described in the IETF standard draft.
  The headers `date` and `x-beacon-user` must be signed.

The Python code in this repository demonstrates how to do this.

## Installation

1. Setup virtualenv or conda environment (your choice)
2. Clone, install dependencies, test
    ```bash
    $ git clone git@github.com:bihealth/varfish-clinical-beacon-client.git
    $ cd varfish-clinical-beacon-client
    $ pip install -r requirements.txt
    ```
3. Test
    ```bash
    $ python clinical-beacon-client.py --help
    ```

## Generate Key

```bash
$ ./clinical-beacon-client.py gen-key
[I 210304 11:49:49 clinical-beacon-client:14] Generating public/private key pair...
[I 210304 11:49:49 clinical-beacon-client:15]   public key:  key_rsa
[I 210304 11:49:49 clinical-beacon-client:21]   private key: key_rsa.pub
[I 210304 11:49:49 clinical-beacon-client:26] ... done generating key pair.
[I 210304 11:49:49 clinical-beacon-client:27] Have a nice day!
$ ls key_rsa*
key_rsa  key_rsa.pub
```

## Register Key

Now you have to register the public key in `key_rsa.pub` with the remote that you want to query.
From this, you obtain a key id, say `test-client`.
You can now contact the beacon.

## Get Beacon Info

```bash
$ ./clinical-beacon-client.py query \
    --key-id test-client \
    --beacon-user testuser@example.com \
    --endpoint https://beacon.example.com/endpoint/
[I 210304 12:09:39 clinical-beacon-client:47] Asking beacon for info...
[I 210304 12:09:39 clinical-beacon-client:69] => OK 200
[I 210304 12:09:39 clinical-beacon-client:70] result below on stdout --8<-- --8<-- --8<--
{
  "id": "com.example.beacon",
  "name": "Example Beacon Site",
  "apiVersion": "v1.0.0",
  "organis": {
    "id": "com.example",
    "name": "Example Org",
    "description": "Just for example..."
  },
  "datasets": [
    {
      "id": "com.example.beacon.ds-1",
      "name": "Dataset",
      "assembly": "GRCh37",
      "description": null
    }
  ]
}
[I 210304 12:09:39 clinical-beacon-client:72] -->8-- -->8-- -->8-- result above on stdout
[I 210304 12:09:39 clinical-beacon-client:86] ... done asking beacon for info.
[I 210304 12:09:39 clinical-beacon-client:87] Have a nice day!
```

## Perform Query

```bash
$ ./clinical-beacon-client.py query \
    --key-id test-client \
    --beacon-user testuser@example.com \
    --endpoint https://beacon.example.com/endpoint/ \
    --variant 1-16977-G-A
[I 210304 12:07:45 clinical-beacon-client:36] Executing query for 1-16977-G-A...
[I 210304 12:07:47 clinical-beacon-client:69] => OK 200
[I 210304 12:07:47 clinical-beacon-client:70] result below on stdout --8<-- --8<-- --8<--
{
  "beaconId": "com.example.beacon",
  "apiVersion": "v1.0.0",
  "exists": true,
  "alleleRequest": {
    "referenceName": "1",
    "referenceBases": "G",
    "start": 16977,
    "alternateBases": "A",
    "assemblyId": "GRCh37"
  },
  "datasetAlleleResponse": null,
  "error": null
}
[I 210304 12:07:47 clinical-beacon-client:72] -->8-- -->8-- -->8-- result above on stdout
[I 210304 12:07:47 clinical-beacon-client:84] ... done executing query.
[I 210304 12:07:47 clinical-beacon-client:87] Have a nice day!
```
