1. Create new python environment (recommended)
2. Then install packages

```
pip install -r requirements.txt

```

----- UPDATES READ ME -----
Starting to keep track of changes startingt today 7 apr 25.

## Base Bot 4.0.2

### BrowserSessionConfig

The `BrowserSessionConfig` is a TypedDict that can be used to configure browser sessions. It has the following optional fields:

- `annual_pdf_filename: Optional[str]`: A custom filename for saving PDFs.
- `original_json: Optional[dict]`: A dictionary containing original JSON data related to the session.

### Usage in call_agent

The `call_agent` method in `browser_client_base_bot` accepts a fourth parameter, which is an object of type `BrowserSessionConfig`. This parameter allows you to configure the browser session with custom settings. This sessions is set on start of browser and is available for retrieval when an cancel or reject commands are received for cleanup and other retry purposes.

### Retry Mechanism
When a task is cancelled, the `BrowserClientBaseBot` sends a chat message with the original JSON received along with a retry code block automatically. This allows for manual retries by providing the necessary context and data to restart the task.

Here is an example of the retry message format:
``task cancelled [json]{original_json}[/json] [Retry]``

### Print Dialog Handler

The `PrintDialogHandler` is an extension that handles system print dialogs during browser automation. When a print action is triggered, this extension will:

1. Select the PDF printer (e.g., "Microsoft Print to PDF").
2. Click Save/Print button to save the PDF.

The output path is determined based on the `custom_downloads_path` specified in the configuration. To use the `PrintDialogHandler`, you need to extend the controller with this handler. 

