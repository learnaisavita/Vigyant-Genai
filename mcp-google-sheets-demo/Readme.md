MCP Host : The AI application.
Examples include VS Code and other AI applications that support MCP. Visual Studio Code can act as an MCP host

MCP Client: The component inside the host responsible for communicating with an MCP serve
r

MCP Server: The program exposing capabilities/data to the AI.
Microsoft describes MCP servers as enabling agents to work with external data sources and capabilities

┌───────────────────────────────┐
│ User                          │
│ "Show sales from Sheet1"      │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ Gemini Agent                  │
│ Decides which tool to call    │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ MCP Client                    │
│ initialize                    │
│ tools/list                    │
│ tools/call                    │
└──────────────┬────────────────┘
               │ stdio
               ▼
┌───────────────────────────────┐
│ MCP Server                    │
│ read_sheet                    │
│ append_row                    │
└──────────────┬────────────────┘
               │ Google API
               ▼
┌───────────────────────────────┐
│ Google Sheets                 │
└───────────────────────────────┘

Gemini understands what the user wants.
MCP client communicates using the MCP contract.
MCP server exposes approved tools.
Google Sheets API performs the underlying operation.

MCP is the integration layer. It does not replace Gemini or the Google Sheets API.

Step-1: Create the environment
mkdir mcp-google-sheets-demo
cd mcp-google-sheets-demo
.\.venv\Scripts\Activate.ps1

Step-2: pip install -r requirements.txt

NOTE: Install NVM manually
install NVM
and check using cli 
node --version
npm --version
npx --version
 
 Step-3: Configure Google Sheets
 
Create or select a Google Cloud project.
Enable the Google Sheets API.
Create a service account.
Create a JSON key for that service account.
Save it locally as:credentials/service-account.json

Step-4: OPen credentials/service-account.json file
{
  "client_email": "your-service-account@project.iam.gserviceaccount.com"
}
Copy only email_id: your-service-account@project.iam.gserviceaccount.com
Share your Google Sheet with that email address.
Give it Viewer permission initially.

Step-5: Edit google sheet with data below
Product     Region     Quantity     Revenue
Laptop      West       3            210000
Monitor     South      5            75000
Keyboard    North      10           30000

Copy Id only from google sheet link
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit >> spreadsheets_values only


Step_6 : Create .env file :
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json
GOOGLE_SPREADSHEET_ID=replace-with-your_actual_spreadsheet_id

GEMINI_API_KEY=replace-with-your-gemini-key
GEMINI_MODEL=replace-with-a-supported-model-name

Step_7:- Execute sheets_server.py using 
mcp dev sheets_server.py


MCP Inspector (client)
        │
        │ tool discovery
        ▼
sheets_server.py (server)
        │
        ├── health_check
        ├── test_sheets_connection
        ├── read_sheet
        └── add


Step-8:- Run server.py file
uv run mcp dev sheets_server.py

MCP Inspector      
       ↓
MCP tool discovery  
       ↓
MCP tool execution 
       ↓
Service account     
       ↓
Spreadsheet ID     
       ↓
Google Sheets API
       ↓
Actual Sheet Data


Verify tools like add >> add 2 values
Test sheet connection
Read sheet >> Sheet1!A1:d4