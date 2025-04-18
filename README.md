# vase

VASE (Versatile Audio Stream Extractor) is a software suite for clipping audio segments from live audio feeds and includes basic media playback functionality for playing audio during those streams.

# Development

To develop this you will need docker.

To run the project, first clone the repo onto your device,

Then, run:

```
docker compose up --build

```

# Deployment

When deploying VASE you may want to run it with some environment variables

ADMIN_PASSWORD - the password used to access the admin controls. This is not secure. Do not use this app for any personally identifiable data please please.
PORT - the port you are running vase on. I recommend 5040.
THREADS - the number of waitress threads to run vase with.
VASE_URL - the url of vase that will be used for copying clip links.

examples of all of these can be found in .env.example
