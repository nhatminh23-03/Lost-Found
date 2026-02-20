# Lost & Found Board

A Flask web app for reporting and browsing lost or found items on campus.  
Built with **Python 3.11+**, **MongoDB Atlas**, and **Cloudflare R2** image storage.

---

## Table of Contents

- [Lost \& Found Board](#lost--found-board)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
    - [1 — Create a virtual environment](#1--create-a-virtual-environment)
    - [2 — Install dependencies](#2--install-dependencies)
    - [3 — Configure environment variables](#3--configure-environment-variables)
    - [4 — Run locally](#4--run-locally)
  - [Smoke Tests](#smoke-tests)
    - [Test 1 — Create a post without an image](#test-1--create-a-post-without-an-image)
    - [Test 2 — Create a post with an image](#test-2--create-a-post-with-an-image)
    - [Test 3 — Feed shows all posts](#test-3--feed-shows-all-posts)
    - [Test 4 — Detail page works](#test-4--detail-page-works)
  - [Troubleshooting](#troubleshooting)
    - [MongoDB connection issues](#mongodb-connection-issues)
    - [Cloudflare R2 errors](#cloudflare-r2-errors)
    - [Image validation errors](#image-validation-errors)
  - [Running with Gunicorn (production-like)](#running-with-gunicorn-production-like)

---

## Project Structure

```
Lost&Found/
├── run.py                  # App entry point
├── run.sh                  # Convenience launcher (dev + prod)
├── requirements.txt
├── .env                    # Your local secrets — never commit this
├── .env.example            # Template with placeholder values
└── app/
    ├── __init__.py         # Flask app factory
    ├── config.py           # All env vars and upload constraints
    ├── routes/posts.py     # Route handlers (feed, new, create, detail)
    ├── services/
    │   ├── db.py           # MongoDB CRUD helpers
    │   └── storage.py      # Cloudflare R2 upload via boto3
    ├── templates/          # Jinja2 HTML templates
    └── static/styles.css   # Plain CSS, no frameworks
```

---

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.11 |
| pip | 23+ |
| MongoDB Atlas | Free tier cluster |
| Cloudflare R2 | Bucket with public access enabled |

---

## Setup

### 1 — Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> **Note:** activate the venv every time you open a new terminal before running the app.  
> To deactivate: `deactivate`

---

### 2 — Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3 — Configure environment variables

Copy the example file and fill in your real values:

```bash
cp .env.example .env
```

Then open `.env` and set each variable:

```dotenv
# Flask
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development
PORT=8080

# MongoDB Atlas
# Full connection string from Atlas → Connect → Drivers
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<AppName>
MONGODB_DB=lost_and_found

# Cloudflare R2
# Found in R2 → Manage R2 API Tokens
R2_ACCESS_KEY_ID=your-r2-access-key-id
R2_SECRET_ACCESS_KEY=your-r2-secret-access-key
# Format: https://<account-id>.r2.cloudflarestorage.com
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_BUCKET_NAME=your-bucket-name
# Public URL from your bucket's public domain (e.g. r2.dev or custom domain)
R2_PUBLIC_BASE_URL=https://pub-<hash>.r2.dev
```

> **Security:** `.env` is listed in `.gitignore` and will never be committed.  
> Never paste real credentials into `.env.example`.

---

### 4 — Run locally

```bash
FLASK_ENV=development bash run.sh
```

Or directly with Python (always runs in debug mode):

```bash
python run.py
```

The app will be available at: **http://localhost:8080**

> If port 8080 is taken, change `PORT=8080` in `.env` to any free port.

---

## Smoke Tests

Verify the app end-to-end after starting it. All steps use only a browser.

### Test 1 — Create a post without an image

1. Open **http://localhost:8080/new**
2. Select **Lost** or **Found**
3. Fill in all required fields: Item Name, Location, Description, Contact
4. Leave the photo field empty
5. Click **Submit Post**
6. **Expected:** redirected to the post detail page showing your entry

---

### Test 2 — Create a post with an image

1. Open **http://localhost:8080/new**
2. Fill in all fields as above
3. Click **Choose File** and select a `.jpg`, `.png`, or `.webp` ≤ 5 MB
4. Click **Submit Post**
5. **Expected:** redirected to the detail page, image is displayed from the R2 public URL

---

### Test 3 — Feed shows all posts

1. Open **http://localhost:8080/**
2. **Expected:** both posts from Tests 1 and 2 appear as cards, newest first
3. If an image was uploaded, the card thumbnail renders correctly

---

### Test 4 — Detail page works

1. From the feed, click any post card
2. **Expected:** full detail page loads at `/posts/<id>` with title, description, location, contact, and image (if present)
3. Clicking **← Back to all posts** returns to the feed

---

## Troubleshooting

### MongoDB connection issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ServerSelectionTimeoutError` | IP not whitelisted | Go to Atlas → Network Access → Add your IP (or `0.0.0.0/0` for dev) |
| `Authentication failed` | Wrong username/password in URI | Re-copy URI from Atlas → Connect → Drivers |
| `MONGODB_URI` missing | `.env` not loaded | Confirm `.env` exists in the project root and `python-dotenv` is installed |
| Wrong database name | `MONGODB_DB` mismatch | Check Atlas for the exact database name (case-sensitive) |

---

### Cloudflare R2 errors

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `NoCredentialsError` | `R2_ACCESS_KEY_ID` or `R2_SECRET_ACCESS_KEY` blank | Generate an R2 API token with **Object Read & Write** permission |
| `EndpointResolutionError` | Incorrect `R2_ENDPOINT_URL` | Must be `https://<account-id>.r2.cloudflarestorage.com` (no bucket name, no trailing slash) |
| `NoSuchBucket` | Bucket name mismatch | Confirm `R2_BUCKET_NAME` matches exactly (case-sensitive) in the Cloudflare dashboard |
| Image uploads succeed but not visible | `R2_PUBLIC_BASE_URL` wrong or bucket not public | Enable public access on the bucket in R2 dashboard; URL should be `https://pub-<hash>.r2.dev` |
| `403 Forbidden` on upload | Token lacks write permission | Create a new API token with **Edit** (read + write) scope for the bucket |

---

### Image validation errors

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `"Image must be jpg, jpeg, png, or webp"` flash | Wrong file type | Convert the file to a supported format before uploading |
| `"Image is too large"` flash or HTTP 413 | File exceeds 5 MB | Compress or resize the image before uploading (e.g. macOS Preview → Export) |
| Image field accepted but no image shown | R2 upload silently failed | Check the Flask console for `R2 upload failed:` log lines; verify R2 credentials |

---

## Running with Gunicorn (production-like)

```bash
gunicorn "run:app" --bind "0.0.0.0:8080" --workers 2
```

---

*CS 4800 — Spring 2026*
