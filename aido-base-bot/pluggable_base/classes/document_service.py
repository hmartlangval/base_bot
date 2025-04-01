import os

def read_pdf_files(folder_path):
    """
    Scans a folder for PDF files, and saves to JSON.
    """
    file_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                file_info = {
                    "path": pdf_path,
                    "filename": file,
                    "property_name": "",  # Initialize all fields to "Not Found"
                    "owner_name": "",
                    "owner_address": "",
                    "property_address": "",
                    "tax_id": "",
                    "status": "New",
                    "downloads_path": "",
                }
                file_list.append(file_info)

    return file_list