# Apple Wallet Pass Certificate Setup Guide

## Why Your Pass Won't Download on iPhone

The main reason your Apple Wallet pass won't download is missing or incorrect certificates. Here's what you need to fix:

### 1. Required Certificate Files

You need these files in your `certs/` directory:
- `certificate.pem` - Your Apple Wallet certificate
- `private.pem` - Your private key

### 2. How to Get the Certificates

#### Step 1: Apple Developer Account
1. Go to [Apple Developer Portal](https://developer.apple.com)
2. Navigate to "Certificates, Identifiers & Profiles"
3. Select "Identifiers" → "Pass Type IDs"
4. Create a new Pass Type ID or use existing one

#### Step 2: Create Pass Type ID
1. Click "+" to create new Pass Type ID
2. Description: "Event Pass"
3. Identifier: `pass.com.oguzhanvarsak.event` (must match your JSON)
4. Enable "Passes" capability

#### Step 3: Create Certificate
1. Select your Pass Type ID
2. Click "Edit"
3. Under "Passes", click "Create Certificate"
4. Follow the certificate creation process
5. Download the certificate

#### Step 4: Convert Certificate Format
```bash
# Convert .cer to .pem
openssl x509 -in certificate.cer -inform DER -out certs/certificate.pem

# Extract private key (if you have .p12 file)
openssl pkcs12 -in certificate.p12 -out certs/private.pem -nodes -clcerts
```

### 3. Update Your Settings

In `tap/settings.py`, update these values with your actual data:

```python
WALLETPASS = {
    "CERT_PATH": str(BASE_DIR / "certs" / "certificate.pem"),
    "KEY_PATH": str(BASE_DIR / "certs" / "private.pem"),
    "KEY_PASSWORD": "your_password_here",  # If your key has a password
    "PASS_TYPE_ID": "pass.com.oguzhanvarsak.event",  # Must match your Apple Developer Pass Type ID
    "TEAM_ID": "YOUR_TEAM_ID",  # Your Apple Developer Team ID
    "ORGANIZATION_NAME": "Oğuzhan Varsak",
}
```

### 4. Web Service Requirements

For passes to work properly, you need:

1. **HTTPS Web Service**: Your server must be accessible via HTTPS
2. **Web Service Endpoints**: 
   - `GET /passes/{serialNumber}` - Get pass data
   - `POST /passes/{serialNumber}/registrations/{deviceLibraryIdentifier}` - Register device
   - `DELETE /passes/{serialNumber}/registrations/{deviceLibraryIdentifier}` - Unregister device
   - `GET /passes/{serialNumber}/latest` - Get latest pass version

### 5. Testing Your Pass

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Visit: `http://localhost:8000/loyalty/test`

3. Create a pass and try downloading it

### 6. Common Issues and Solutions

#### Issue: "Safari cannot install this pass"
- **Cause**: Invalid or missing certificates
- **Solution**: Ensure certificate files exist and are properly formatted

#### Issue: "Pass type identifier not found"
- **Cause**: Pass type identifier doesn't match Apple Developer account
- **Solution**: Update `PASS_TYPE_ID` in settings to match your Apple Developer Pass Type ID

#### Issue: "Team identifier not found"
- **Cause**: Team ID doesn't match your Apple Developer account
- **Solution**: Update `TEAM_ID` in settings with your actual Apple Developer Team ID

#### Issue: Pass downloads but shows as invalid
- **Cause**: Web service URL is not accessible or not HTTPS
- **Solution**: Ensure your web service is running on HTTPS and accessible

### 7. Production Deployment

For production, you need:
1. Valid SSL certificate for your domain
2. Proper web service endpoints implemented
3. Database to store pass registrations
4. Push notification certificates for pass updates

### 8. Quick Test

To test if your certificates work:

```bash
# Check if certificate files exist
ls -la certs/

# Test certificate validity
openssl x509 -in certs/certificate.pem -text -noout

# Test private key
openssl rsa -in certs/private.pem -check
```

### 9. Next Steps

1. Get your Apple Developer certificates
2. Place them in the `certs/` directory
3. Update the settings with your actual values
4. Test the pass download
5. Implement web service endpoints for full functionality

Remember: Apple Wallet passes require valid Apple Developer certificates to work. Without them, Safari will refuse to install the pass. 