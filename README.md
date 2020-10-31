# ytmdl

[![codecov](https://codecov.io/gh/jaeseopark/ytmdl/branch/master/graph/badge.svg)](https://codecov.io/gh/jaeseopark/ytmdl)

Uses GCP PubSub & Cloud Functions to continuously download music from YouTube. All Liked videos get saved to the designated Google Drive location.

### Test

```bash
pytest test/unit         # isolated test cases; safe to run in any environment
pytest test/integration  # requires LOCAL_SERVICE_SECRETS and a 'default' user in Firestore
pytest test/manual       # requires LOCAL_SERVICE_SECRETS, a 'default' user in Firestore, and manual validation
```

### Runtime environment

```bash
docker build -t ytmdl .  # see Dockerfile for details
docker run -it ytmdl
```

### Architecture

![Sequence Diagram](https://ytmdl.s3-us-west-2.amazonaws.com/ytmdl-sequence.png)
