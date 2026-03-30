# Production Deployment Setup

## 🏢 Service Principal Setup (Recommended for Production)

### Why Service Principals?

✅ **Not tied to individual users** - No disruption when employees leave
✅ **Fine-grained permissions** - Only give what's needed
✅ **Auditable** - Track all deployments
✅ **Industry standard** - Used by enterprises worldwide

---

## Option 1: Azure Databricks (Service Principal)

### Step 1: Create Azure AD App Registration

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Name: `databricks-cicd-app`
4. Click **Register**
5. Copy the **Application (client) ID** - this is your `CLIENT_ID`

### Step 2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Description: `GitHub Actions`
4. Expiration: 24 months (or as per policy)
5. Click **Add**
6. Copy the **Value** - this is your `CLIENT_SECRET` (you won't see it again!)

### Step 3: Add Service Principal to Databricks

```bash
# In Databricks workspace
1. Go to Settings → Admin Console → Service Principals
2. Click "Add Service Principal"
3. Application ID: <paste your CLIENT_ID>
4. Click "Add"
5. Grant permissions: Workspace access, SQL access (as needed)
```

### Step 4: GitHub Secrets for Azure

Add these secrets to your GitHub repo:

```
DATABRICKS_HOST = https://adb-<workspace-id>.<region>.azuredatabricks.net
DATABRICKS_CLIENT_ID = <your-application-client-id>
DATABRICKS_CLIENT_SECRET = <your-client-secret>
```

---

## Option 2: AWS Databricks (Service Principal)

### Step 1: Create Service Principal in Databricks

```bash
# Using Databricks CLI
databricks service-principals create \
  --display-name "GitHub Actions CI/CD"
```

### Step 2: Generate OAuth Secret

```bash
# Create OAuth secret for the service principal
databricks service-principals secrets create \
  --service-principal-id <SERVICE_PRINCIPAL_ID>
```

### Step 3: Assign Permissions

1. Go to Databricks workspace → **Admin Console**
2. Select **Service Principals**
3. Find your service principal
4. Grant permissions:
   - Workspace access
   - SQL warehouse access
   - Create Apps permission

### Step 4: GitHub Secrets for AWS

```
DATABRICKS_HOST = https://<workspace-url>.cloud.databricks.com
DATABRICKS_CLIENT_ID = <service-principal-id>
DATABRICKS_CLIENT_SECRET = <oauth-secret>
```

---

## Option 3: Development/Testing (PAT)

For development or personal projects, you can use Personal Access Tokens:

### GitHub Secrets (Development Only)

```
DATABRICKS_HOST = https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN = dapi1234567890abcdef...
```

**⚠️ Warning**: PAT expires when:
- Token lifetime ends
- User leaves organization
- Password changes

---

## How the Workflow Decides

The updated workflow automatically detects which method to use:

```yaml
# If DATABRICKS_CLIENT_ID exists → Use Service Principal
# If not → Fall back to PAT
```

You can start with PAT and upgrade to Service Principal later!

---

## Verification

After setting up secrets, trigger a deployment:

```bash
# Make a small change
echo "# Test" >> README.md
git add .
git commit -m "Test deployment"
git push
```

Then check:
1. **GitHub Actions tab** - See deployment logs
2. **Databricks Apps** - Verify app is running

---

## Best Practices

### ✅ DO:
- Use Service Principals in production
- Rotate secrets regularly
- Use separate service principals for dev/prod
- Set appropriate expiration dates
- Monitor deployment logs

### ❌ DON'T:
- Use personal access tokens in production
- Share tokens between projects
- Commit secrets to Git
- Give overly broad permissions

---

## Security Comparison

 Method | Development | Production | Enterprise |
--------|-------------|------------|------------|
 Personal Access Token | ✅ Good | ⚠️ Risky | ❌ No |
 Service Principal | ✅ Good | ✅ Good | ✅ Best |
 OIDC (Keyless) | ✅ Good | ✅ Best | ✅ Best |

---

## Need Help?

- [Databricks Service Principals Docs](https://docs.databricks.com/en/administration-guide/users-groups/service-principals.html)
- [Azure AD App Registration](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
