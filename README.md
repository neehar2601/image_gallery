# image_gallery
# 📸 Dynamic Image Gallery with Amazon S3  

This project demonstrates two approaches to building an **image gallery hosted on Amazon S3**.  

- **Static JSON Index Method** – simple, low-cost, and fast.  
- **Dynamic Serverless Method (Lambda + API Gateway)** – real-time image listing.  

---

## 🚀 1. Static JSON Index Method  

### 🔹 Architecture
   - One **S3 bucket** hosts both website and images.  
   - Images are organized in **date-based folders**:  
   - s3://my-gallery/images/2025-08-29/
   - A **JSON index file** (`gallery-index.json`) is generated and uploaded to the bucket.  
   - Frontend (`index.html + script.js`) reads the JSON and displays images.  



### 🔹 Files
```
/static-gallery
│── index.html # Frontend HTML
│── script.js # Fetch & render images from JSON
│── style.css # Styling
│── generate_index.py # Python script to generate gallery-index.json
```



### 🔹 Steps
1. **Organize Images**
   - Upload images into folders like `/images/YYYY-MM-DD/` in your S3 bucket.

2. **Generate JSON Index**
   ```bash
   python generate_index.py --bucket my-gallery
   ```
### sample JSON:
```bash
{
  "2025-08-29": [
    "https://my-gallery.s3.amazonaws.com/images/2025-08-29/img1.jpg",
    "https://my-gallery.s3.amazonaws.com/images/2025-08-29/img2.jpg"
  ]
}
```
3. **Upload Website**
   ```bash
   aws s3 sync ./static-gallery s3://my-gallery --acl public-read
   ```
4.**Enable Static Website Hosting**
   - In the S3 bucket → Properties → enable Static Website Hosting.
   - Use index.html as the entry point.

✅ Your static gallery is live!

***
## ⚡ 2. Dynamic Lambda + API Gateway Method
### 🔹 Architecture

   - Images still stored in date-based folders in S3.
   - A Lambda function dynamically lists objects.
   - API Gateway (HTTP API) exposes /images/{date} endpoint.
   - Frontend fetches images from API Gateway instead of static JSON.

### 🔹 Files
```
/dynamic-gallery
│── index.html         # Frontend HTML
│── script.js          # Fetch & render images from API Gateway
│── lambda_function.py # Lambda code for dynamic listing
|── s3Readaccess.json  #policy document to grant required permission to lambda function
```
### 🔹 Steps
1. **Create IAM Role for Lambda**
   - Attach AmazonS3ReadOnlyAccess policy.

2. **Deploy Lambda**
   - Runtime: Python 3.9 or higher.
   - Upload lambda_function.py or copy paste the code.

3. **API Gateway Setup**
   - Create an HTTP API.
   - Add route: GET /images/{date} → Integration = Lambda.
   - Deploy to stage (default or prod).

4. **Upload the Frontend to S3**
   - Enable static website hosting
  
✅ Your dynamic gallery updates in real-time as new images are uploaded.

---

## 🌍 3. CloudFront Security & CDN (Recommended)

To secure the gallery and improve performance globally, you can migrate from a public S3 bucket to a **private S3 bucket served via CloudFront**.

### 🔹 Architecture
- **CloudFront Distribution** acts as the global CDN.
- **S3 Origin Access Control (OAC)** allows CloudFront to read from the private S3 bucket.
- **API Gateway Behavior** routes dynamic image API requests to the Lambda function.

### 🔹 Steps to Migrate
1. **S3 Hardening**: Block ALL public access on the S3 bucket and disable Static Website Hosting.
2. **Bucket Policy**: Add a policy allowing `s3:GetObject` and `s3:ListBucket` strictly for the CloudFront Service Principal using the OAC condition.
3. **CloudFront Configuration**:
   - Create a distribution with two Origins: S3 (with OAC) and API Gateway.
   - Add Behaviors: 
     - **Path `/images`** → routes to API Gateway (Caching Disabled).
     - **Path `/*` (Default)** → routes to S3 OAC (Caching Optimized).
4. **Update Lambda & Frontend**:
   - Modify the Lambda function to return **S3 object keys** instead of complete direct S3 URLs.
   - Update the frontend to use CloudFront URLs based on S3 keys.

This approach ensures zero direct public S3 access and speeds up image delivery globally. For the complete, detailed migration guide, check out the [S3 Private Migration Complete Guide](./Cloudfront/s3-private-migration-complete-guide.md).

---

## 🔐 Security Considerations
- **Restrict public read access** → serve via CloudFront (as detailed above).  
- **CORS** → configure in API Gateway or return headers in Lambda.  
- **IAM Policy** → grant Lambda only `s3:ListBucket` and `s3:GetObject`.  

---

## 📊 Comparison

| Feature          | Static JSON Index       | Lambda + API Gateway   |
|------------------|------------------------|-------------------------|
| **Complexity**   | Low                    | Medium/High             |
| **Performance**  | Very fast (cached JSON) | Slightly slower (real-time) |
| **Cost**         | Almost free            | Pay-per-invoke          |
| **Updates**      | Manual JSON regen      | Automatic, real-time    |
| **Best for**     | Small galleries, rarely updated | Larger galleries, frequent uploads |

---

  

  
