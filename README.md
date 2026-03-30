# Data Explorer - Databricks App

A full-stack web application for exploring and querying Databricks data, built with Flask backend and vanilla JavaScript frontend.

## 🎯 Features

* **Interactive Data Browser**: Navigate through catalogs, schemas, and tables
* **Quick Table Preview**: Load and display table data with a single click
* **Custom SQL Queries**: Execute custom SQL queries directly from the UI
* **Responsive Design**: Modern, professional UI that works on all devices
* **Real-time Status Updates**: Clear feedback on operations and errors
* **CI/CD Ready**: Automated deployment via GitHub Actions

## 📁 Project Structure

```
data-explorer-app/
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions workflow
├── app.py                      # Flask backend API
├── app.yaml                    # Databricks App configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── static/                     # Frontend assets
    ├── index.html              # Main HTML page
    ├── style.css               # Styles
    └── app.js                  # Frontend logic
```

## 🚀 Deployment Options

### Option 1: Automated GitHub Deployment (Recommended)

This method automatically deploys your app whenever you push to the main branch.

#### Step 1: Push Code to GitHub

```bash
# Initialize git repository (if not already done)
cd data-explorer-app
git init

# Add all files
git add .
git commit -m "Initial commit: Data Explorer app"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/data-explorer-app.git

# Push to GitHub
git push -u origin main
```

#### Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

   **DATABRICKS_HOST**
   ```
   https://your-workspace.cloud.databricks.com
   ```

   **DATABRICKS_TOKEN**
   ```
   your-personal-access-token
   ```

   To create a personal access token:
   - Go to Databricks → **Settings** → **Developer** → **Access tokens**
   - Click **Generate new token**
   - Copy the token (you won't see it again!)

#### Step 3: Deploy Automatically

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will automatically:
- Trigger on every push to `main` or `master` branch
- Install dependencies
- Upload code to Databricks workspace
- Create or update the Databricks App
- Start the app

You can also trigger deployment manually:
1. Go to **Actions** tab in GitHub
2. Select **Deploy Databricks App** workflow
3. Click **Run workflow**

#### Step 4: Monitor Deployment

- Check the **Actions** tab in GitHub to see deployment progress
- Logs show each step of the deployment
- Once complete, access your app via Databricks Apps UI

---

### Option 2: Using Databricks CLI

1. Install Databricks CLI if you haven't already:
   ```bash
   pip install databricks-cli
   ```

2. Configure your Databricks connection:
   ```bash
   databricks configure --token
   ```

3. Navigate to the app directory:
   ```bash
   cd /Workspace/Users/your.email@domain.com/data-explorer-app
   ```

4. Deploy the app:
   ```bash
   databricks apps create data-explorer
   databricks apps deploy data-explorer --source-code-path .
   ```

---

### Option 3: Using Databricks UI

1. Go to your Databricks workspace
2. Navigate to **Apps** in the left sidebar
3. Click **Create App**
4. Select **Custom** and provide:
   - **Name**: data-explorer
   - **Source Code Path**: `/Workspace/Users/your.email@domain.com/data-explorer-app`
5. Click **Create** and wait for deployment

## 🔧 Configuration

### SQL Warehouse

The app requires a SQL Warehouse for querying data. Update `app.yaml` if you want to use a different warehouse:

```yaml
resources:
  sql_warehouse:
    name: "Your Warehouse Name"  # Change this
    permission: "CAN_USE"
```

### Environment Variables

The following environment variables are automatically populated by Databricks Apps:
* `DATABRICKS_SERVER_HOSTNAME`: Your workspace hostname
* `DATABRICKS_HTTP_PATH`: SQL Warehouse HTTP path
* `DATABRICKS_TOKEN`: Authentication token

## 💡 Usage

### Browse Data
1. Select a **Catalog** from the dropdown
2. Select a **Schema**
3. Select a **Table**
4. Click **Load Table Data** to preview the first 100 rows

### Custom SQL Query
1. Click **Custom SQL Query** button
2. Enter your SQL query
3. Click **Execute Query**
4. View results in the table below

## 🛠️ Customization

### Modify Row Limit

To change the default row limit (currently 100), edit `app.py`:

```python
# In loadTableData function
limit = data.get('limit', 100)  # Change 100 to your desired limit
```

### Add New Endpoints

Add new API endpoints in `app.py`:

```python
@app.route('/api/your-endpoint')
def your_endpoint():
    # Your logic here
    return jsonify({'data': 'value'})
```

### Customize Styling

Modify `static/style.css` to change colors, fonts, or layout:

```css
/* Example: Change primary color */
.btn-primary {
    background: linear-gradient(135deg, #your-color 0%, #your-color-2 100%);
}
```

### Add Frontend Features

Extend `static/app.js` with new functionality:

```javascript
// Example: Add export functionality
function exportToCSV(data) {
    // Your export logic
}
```

## 🔄 Development Workflow

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run locally: `python app.py`

### Making Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Test locally
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request on GitHub
7. After merge to main, automatic deployment triggers

### Deployment Stages

**Development** → **GitHub** → **GitHub Actions** → **Databricks Workspace** → **Databricks App**

## 🔐 Security

* Authentication is handled automatically by Databricks Apps
* SQL injection is prevented by using parameterized queries
* CORS is configured for same-origin requests
* GitHub secrets store sensitive credentials securely
* Personal access tokens should have minimal required permissions

## 📊 API Endpoints

* `GET /api/health` - Health check
* `GET /api/catalogs` - List all catalogs
* `GET /api/schemas/<catalog>` - List schemas in a catalog
* `GET /api/tables/<catalog>/<schema>` - List tables in a schema
* `POST /api/query` - Query a table with limit
* `POST /api/custom-query` - Execute custom SQL query

## 🐛 Troubleshooting

### App won't start
* Check that `app.yaml` references a valid SQL Warehouse
* Verify all files are in the correct directory structure
* Check app logs in Databricks UI

### GitHub Actions failing
* Verify GitHub secrets are set correctly (DATABRICKS_HOST and DATABRICKS_TOKEN)
* Check workflow logs in GitHub Actions tab
* Ensure personal access token has not expired
* Verify Databricks CLI commands in workflow

### Database connection errors
* Ensure the SQL Warehouse is running
* Verify you have proper permissions to access the data

### Frontend not loading
* Clear browser cache
* Check browser console for JavaScript errors
* Verify static files are in the `static/` directory

## 📝 License

This is a starter template - customize it for your needs!

## 🤝 Contributing

Feel free to modify and extend this application for your specific use case.

---

**Built with ❤️ for Databricks**
