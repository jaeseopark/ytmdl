# ytmdl

Continuously saves all of your Liked videos on YouTube to your Google Drive as audio files (m4a).

### Architecture

![Sequence Diagram](https://ytmdl.s3-us-west-2.amazonaws.com/ytmdl-sequence.png)

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
