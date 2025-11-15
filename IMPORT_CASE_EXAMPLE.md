# Import Case Command Example

This document demonstrates the usage of the new `import-case` command.

## Basic Usage

Import a case from a Salesforce URL:

```bash
kase import-case https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view
```

## With Options

### Show Browser Window

If you want to see the browser window (useful for debugging or understanding the login process):

```bash
kase import-case https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view --show-browser
```

### Custom Case Directory

Specify a custom directory for storing cases:

```bash
kase import-case https://acme.my.salesforce.com/5001234567890AB --case-dir /path/to/cases
```

## Example Output

When you run the command, you'll see output like this:

```
Importing case from: https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view
Navigating to https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view

Login required. Please complete the login process in the browser.
Waiting for login to complete...

Extracted case ID: 5001234567890AB

Case imported successfully:
  SF ID: 5001234567890AB
  Title: Customer Cannot Access Dashboard
  Description: Customer reports that they cannot access their dashboard after the latest update...

Case created at: /home/user/cases/5001234567890AB
```

## Workflow

1. **Navigate to URL**: The command opens a headless browser and navigates to the Salesforce case URL
2. **Login Detection**: If not logged in, the browser will wait for you to complete the login process
3. **Data Extraction**: Once authenticated, the command extracts:
   - Case ID from the URL
   - Case title (Subject field)
   - Case description (Description field)
4. **Case Creation**: Creates a new case directory with the structure:
   ```
   ~/cases/
   └── 5001234567890AB/
       └── case.json
   ```

## Case JSON Structure

The created `case.json` file follows the existing kase format:

```json
{
    "title": "Customer Cannot Access Dashboard",
    "desc": "Customer reports that they cannot access their dashboard after the latest update. They receive an error message 'Access Denied' when trying to log in. This started happening after yesterday's deployment.",
    "sf": "5001234567890AB",
    "lp": ""
}
```

## Troubleshooting

### Case ID Not Found

If the case ID cannot be extracted from the URL, check that:
- The URL is a valid Salesforce case URL
- The URL contains a 15 or 18 character Salesforce ID

### Login Timeout

If login times out (default: 5 minutes), you can:
- Run with `--show-browser` to see what's happening
- Check your Salesforce credentials
- Ensure you have access to the case

### Title/Description Not Found

If the case data cannot be extracted:
- The page selectors may need updating for your Salesforce version
- Run with `--show-browser` to verify the page loaded correctly
- Check that you have permission to view the case

## Integration with Other Commands

After importing a case, you can use it with other kase commands:

```bash
# Query and select the imported case
kase query

# Navigate to the case directory (with shell integration)
jk
```
