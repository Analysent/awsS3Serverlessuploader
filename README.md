# AWS S3 Serverless Uploader

A complete end-to-end serverless file uploader that lets users upload images, PDFs, and documents to Amazon S3 from a web page.

## Architecture

- **Frontend**: Static HTML/CSS/JavaScript page
- **API**: Amazon API Gateway
- **Compute**: AWS Lambda (Python)
- **Storage**: Amazon S3
- **Infrastructure as Code**: AWS SAM

## Flow

1. User opens the web page.
2. User selects a file.
3. Frontend calls the `/presign` API endpoint.
4. Lambda validates the request and returns a presigned S3 upload URL.
5. Browser uploads the file directly to S3.
6. The uploaded object is stored in a private S3 bucket.

This avoids sending the full file through Lambda.

---

## Project structure

```text
.
├── backend/
│   ├── src/
│   │   └── app.py
│   ├── events/
│   │   └── presign-event.json
│   ├── template.yaml
│   └── samconfig.toml.example
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── .gitignore
└── README.md
```

---

## Features

- Upload images and common documents
- Presigned URL uploads directly to S3
- Private upload bucket by default
- Basic drag-and-drop upload UX
- Upload progress bar
- File type allow list
- CORS enabled for frontend access
- SAM template for one-command deployment

---

## Supported file types

- JPG / JPEG
- PNG
- GIF
- WEBP
- PDF
- TXT
- DOC / DOCX
- XLS / XLSX

You can extend the allow list in `backend/src/app.py`.

---

## Prerequisites

- AWS account
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.12

---

## Deploy backend

From the repository root:

```bash
cd backend
sam build
sam deploy --guided
```

Suggested values:

- Stack name: `aws-s3-serverless-uploader`
- Region: your preferred AWS region
- Parameter `UploadBucketName`: a globally unique bucket name such as `analysent-serverless-uploader-demo-12345`
- Parameter `AllowedOrigin`: the exact origin of your frontend, such as `http://localhost:8080` for local testing or your deployed site URL

After deployment, note the output values:

- `PresignApiUrl`
- `WebsiteBucketName`
- `UploadBucketNameOut`

---

## Configure frontend

Open `frontend/app.js` and replace:

```javascript
const API_URL = "REPLACE_WITH_YOUR_PRESIGN_API_URL";
```

with the deployed `PresignApiUrl`.

---

## Run frontend locally

You can use a simple static web server.

### Python

```bash
cd frontend
python -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

Make sure your backend `AllowedOrigin` matches your local URL.

---

## Optional: host frontend in S3

You can upload the files from `frontend/` to a separate S3 bucket configured for static website hosting, or serve them using CloudFront.

---

## Security notes

For demo simplicity, the sample is lightweight. For production, consider adding:

- Amazon Cognito authentication
- Per-user folder prefixes like `uploads/{userId}/...`
- CloudFront in front of the site
- Malware scanning via S3 event + Lambda/AV workflow
- Size limits and content validation
- Metadata persistence in DynamoDB
- Private download flow using signed URLs

---

## Example upload object key

```text
uploads/2026/03/<uuid>-myfile.pdf
```

---

## API request format

`POST /presign`

```json
{
  "fileName": "example.pdf",
  "contentType": "application/pdf"
}
```

Response:

```json
{
  "uploadUrl": "https://...",
  "fileKey": "uploads/...",
  "expiresIn": 300
}
```

---

## Next improvements

- Multiple file upload
- Thumbnail previews for images
- Authentication and user scoping
- Admin upload history view
- Metadata store in DynamoDB
- S3 event processing pipeline

---

## License

MIT
