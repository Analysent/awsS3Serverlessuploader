# AWS S3 Serverless Uploader + Bedrock-Ready Dashboard

A complete end-to-end serverless upload platform that lets users upload images, PDFs, and common documents from a web page directly to Amazon S3 using presigned URLs, then processes uploaded objects into a metadata dashboard and an AI-ready enrichment pipeline.

## What this gives you

- Static web app deployable to GitHub Pages
- API Gateway + Lambda backend
- Direct browser-to-S3 uploads using presigned URLs
- DynamoDB-backed upload metadata dashboard
- Event-driven post-upload processing
- Bedrock-ready enrichment hook for future AI tagging/classification
- Security and DevSecOps starter files

## Architecture

1. Frontend web page hosted on GitHub Pages or any static host
2. API Gateway calls Lambda for `/presign`
3. Lambda returns a presigned S3 upload URL
4. Browser uploads file directly to S3
5. S3 object-created event triggers post-processing Lambda through EventBridge
6. Processor extracts metadata and stores it in DynamoDB
7. Frontend dashboard reads upload metadata via `/uploads`

## Project structure

```text
awsS3Serverlessuploader/
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── codeql.yml
│       └── pages.yml
├── backend/
│   ├── events/
│   │   └── presign-event.json
│   ├── samconfig.toml.example
│   ├── src/
│   │   ├── app.py
│   │   ├── list_uploads.py
│   │   └── processor.py
│   └── template.yaml
├── frontend/
│   ├── app.js
│   ├── config.js
│   ├── index.html
│   └── styles.css
├── .gitignore
├── SECURITY.md
└── README.md
```

## Features

- Drag-and-drop upload area
- Multi-file upload
- Upload progress bars
- Image previews
- Dashboard cards for uploaded files
- File type allow list
- File size validation
- Filename sanitization
- Private S3 bucket with blocked public access
- DynamoDB metadata store
- GitHub Pages workflow
- GitHub CodeQL workflow
- Dependabot config

## Supported file types

- image/jpeg
- image/png
- image/gif
- image/webp
- application/pdf
- text/plain
- application/msword
- application/vnd.openxmlformats-officedocument.wordprocessingml.document
- application/vnd.ms-excel
- application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

## Deploy backend

Prerequisites:
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.12 available

Deploy:
```bash
cd backend
sam build
sam deploy --guided
```

Suggested guided answers:
- Stack name: `aws-s3-serverless-uploader`
- AWS Region: your preferred region
- UploadBucketName: globally unique, for example `analysent-serverless-uploader-12345`
- AllowedOrigin: your GitHub Pages URL, for example `https://analysent.github.io`
- MaxFileSizeMb: `10`

After deploy, note the outputs:
- `ApiBaseUrl`
- `PresignApiUrl`
- `UploadsApiUrl`
- `UploadBucketNameOut`
- `MetadataTableNameOut`

## Configure frontend

Edit `frontend/config.js`:

```javascript
window.S3_UPLOADER_CONFIG = {
  API_BASE_URL: "PASTE_API_BASE_URL_HERE"
};
```

If your GitHub Pages site is at `https://analysent.github.io/awsS3Serverlessuploader/`, the frontend will call:
- `${API_BASE_URL}/presign`
- `${API_BASE_URL}/uploads`

## GitHub Pages setup

Push these files to your repository, then in GitHub:
1. Open **Settings**
2. Open **Pages**
3. Set **Source** to **GitHub Actions**

The included workflow publishes the `frontend/` directory.

Your expected URL will be:
```text
https://analysent.github.io/awsS3Serverlessuploader/
```

## Local frontend testing

```bash
cd frontend
python -m http.server 8080
```

Then open:
```text
http://localhost:8080
```

Make sure `AllowedOrigin` matches `http://localhost:8080` while testing.

## Bedrock-ready processing

The processor currently stores upload metadata to DynamoDB and includes a clear hook for Bedrock-based enrichment. Example future extensions:
- document type classification
- summarization of uploaded text/PDF content
- compliance/risk tagging
- image description or categorization

## Security notes

Included:
- S3 public access blocked
- S3 encryption enabled
- CORS narrowed by parameter
- allow-listed content types
- client-side file size checks
- server-side file size checks for presign requests
- filename normalization
- CodeQL for Python and JavaScript
- Dependabot for GitHub Actions

Recommended next improvements:
- Amazon Cognito authentication
- per-user folder prefixes like `uploads/{userId}/...`
- malware scanning workflow
- CloudFront signed download path
- metadata expansion in DynamoDB
- Bedrock model integration
- OpenSearch / analytics layer
- QuickSight or Streamlit analytics dashboard

## Phone-friendly repo update

You do **not** need to delete your repository.

From phone, the simplest path is:
1. Download and unzip this package
2. Open your GitHub repository
3. Upload the files, preserving the folder structure
4. Replace the existing partial files
5. Commit the changes

## Portfolio positioning

You can describe this as:

> Built a secure serverless ingestion and AI-ready processing platform using AWS S3, API Gateway, Lambda, EventBridge, and DynamoDB, with a modern GitHub Pages frontend and Bedrock-ready enrichment hooks for document intelligence workflows.
