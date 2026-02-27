# PS2 API Endpoints Reference

## Dataset Management

### 1. Upload CSV
**POST** `/upload`

Upload a CSV file and create a new dataset.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: CSV file
  - `dataset_name`: Unique name for the dataset (alphanumeric and underscores only)

**Response:**
```json
{
  "message": "File uploaded and data loaded successfully",
  "dataset_name": "sales_data",
  "columns": ["product", "revenue", "date"],
  "rows_loaded": 1000
}
```

---

### 2. List All Datasets (Sources Panel)
**GET** `/datasets`

Get all uploaded datasets for the left "Sources" panel.

**Response:**
```json
[
  {
    "id": 1,
    "name": "sales_data",
    "file_name": "sales.csv",
    "row_count": 1000,
    "upload_date": "2026-02-27T10:30:00"
  },
  {
    "id": 2,
    "name": "customer_data",
    "file_name": "customers.csv",
    "row_count": 500,
    "upload_date": "2026-02-27T11:00:00"
  }
]
```

---

### 3. Get Dataset Metadata (Table Metadata Panel)
**GET** `/datasets/{dataset_name}/metadata`

Get detailed metadata for the right "Table Metadata" panel.

**Response:**
```json
{
  "name": "sales_data",
  "table_name": "dataset_sales_data",
  "file_name": "sales.csv",
  "row_count": 1000,
  "column_count": 5,
  "file_size": 52480,
  "upload_date": "2026-02-27T10:30:00",
  "columns": ["product", "revenue", "date", "region", "quantity"]
}
```

---

### 4. Delete Dataset
**DELETE** `/datasets/{dataset_name}`

Delete a dataset and its associated table.

**Response:**
```json
{
  "message": "Dataset 'sales_data' deleted successfully"
}
```

---

## Query (Chat Interface)

### 5. Query Dataset
**POST** `/query`

Ask a natural language question about a specific dataset.

**Request:**
```json
{
  "question": "What is the total revenue?",
  "dataset_name": "sales_data"
}
```

**Response:**
```json
{
  "answer": "The total revenue is $125,000 across all products.",
  "sql_query": "SELECT SUM(revenue) as total_revenue FROM dataset_sales_data",
  "data": [
    {
      "total_revenue": 125000
    }
  ]
}
```

**Example with multiple rows:**
```json
{
  "answer": "The dataset contains 5 products with varying revenue levels.",
  "sql_query": "SELECT product, revenue FROM dataset_sales_data",
  "data": [
    {"product": "Widget A", "revenue": 25000},
    {"product": "Widget B", "revenue": 30000},
    {"product": "Widget C", "revenue": 20000},
    {"product": "Widget D", "revenue": 35000},
    {"product": "Widget E", "revenue": 15000}
  ]
}
```

**Key Changes:**
- `data` is now an array of objects (JSON format) instead of separate `columns` and `rows`
- Each row is a dictionary with column names as keys
- Much easier to work with in frontend (no need to zip columns and rows)
- `answer` is now concise (1-3 sentences) and doesn't include the full table

---

## UI Integration Guide

### Left Panel - Sources
1. Call `GET /datasets` on page load
2. Display list of datasets
3. Allow user to select a dataset
4. On selection, call `GET /datasets/{name}/metadata` to populate right panel

### Middle Panel - Chat
1. User types question in input
2. Send `POST /query` with selected dataset_name
3. Display answer as text
4. Display table with columns and rows
5. Optional: Add visualization button

### Right Panel - Table Metadata
1. Display metadata from `GET /datasets/{name}/metadata`
2. Show:
   - Column names
   - Row count
   - File size (convert bytes to KB/MB)
   - Upload date
   - Other metadata

---

## Example Frontend Flow

```javascript
// 1. Load datasets on mount
const datasets = await fetch('/datasets').then(r => r.json());

// 2. User selects a dataset
const selectedDataset = 'sales_data';
const metadata = await fetch(`/datasets/${selectedDataset}/metadata`).then(r => r.json());

// 3. User asks a question
const response = await fetch('/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What is the average revenue?',
    dataset_name: selectedDataset
  })
}).then(r => r.json());

// Display response.answer (concise summary)
// Display response.data as a table (array of objects)
// Example: response.data = [{ product: "Widget A", revenue: 25000 }, ...]
```

---

## Frontend Table Rendering

The new `data` format makes it super easy to render tables:

```javascript
// Get column names from first row
const columns = response.data.length > 0 ? Object.keys(response.data[0]) : [];

// Render table
<table>
  <thead>
    <tr>
      {columns.map(col => <th key={col}>{col}</th>)}
    </tr>
  </thead>
  <tbody>
    {response.data.map((row, i) => (
      <tr key={i}>
        {columns.map(col => <td key={col}>{row[col]}</td>)}
      </tr>
    ))}
  </tbody>
</table>
```
