# Appointment Manager Bot

This bot utilizes LLM's (your choice) along with vocode and twillio to create a bot capable of creating an appointment booking for a doctor

## Pre-reqs

Assuming you have homebrew:

```bash
brew install python@3.9
brew install ngrok/ngrok/ngrok
brew install ffmpeg
brew install redis
```

Also download docker and spin it up.

## To Run

Follow these pre-req steps: https://docs.vocode.dev/telephony including:

```cp .env.template .env```
and setting all the base variables needed.


After installing pre-reqs/setting up environmental variables and assuming you have docker (if not, download docker and spin it up), in one terminal init ngrok via:

```bash
ngrok http 3000
```

and in the other terminal run:

```bash
docker build -t appointment-manager .
docker-compose up
```
