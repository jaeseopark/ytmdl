# ytmdl

Converts all of your Liked videos on YouTube to audio files and saves them to your Google Drive. The delivery happens on an ongoing basis.

### Architecture

(Sequence diagram coming soon...)

ytmdl is designed to run on Google Cloud Platform. Here are the major components that power the system:

* Cloud Scheduler
  * 5-min interval
* Firestore
  * `config.{app}`
  * `users.{user}.videos.{video}`
* Cloud Functions
  * [`iterate_users`](ytmdl/iterate_users.py) Triggered by Cloud Scheduler
  * [`process_user`](ytmdl/process_user.py) Triggered by Firestore `config.{app}`
  * [`process_video`](ytmdl/process_video.py) Triggered by Firestore `users.{user}.videos.{video}`

### Test

```bash
pytest test/unit         # isolated test cases; safe to run in any environment
pytest test/integration  # requires LOCAL_SERVICE_SECRETS
pytest test/manual       # requires LOCAL_SERVICE_SECRETS and manual validation
```

### Runtime environment

```bash
docker build -t ytmdl .  # see Dockerfile for details
docker run -it ytmdl
```
