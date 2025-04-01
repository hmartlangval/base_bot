import io
import base64
import fitz  # PyMuPDF
from PIL import Image
import os
import requests
from datetime import datetime
import pytesseract

class PdfToImage:
    def __init__(self):
        pass
    
    
    @staticmethod
    def get_file_name_from_path(pdf_path):
        return os.path.basename(pdf_path).rsplit('.', 1)[0]
    
    @staticmethod
    def pdf_page_to_base64_from_path(pdf_path, page=1, size=(600, 800), quality=100):
        """Converts a PDF page from a local path to base64-encoded JPEG."""
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            if page > len(doc):
                return None
            
            # Get the page
            page_obj = doc[page - 1]
            
            # Convert to image
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(size[0]/page_obj.rect.width, size[1]/page_obj.rect.height))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="JPEG", quality=quality)
            
            # Debug: Save image to current directory
            # print("Current working directory:", os.getcwd())
            # print("Attempting to save debug image...")
            # img.save("debug_image.jpg", format="JPEG", quality=quality)
            # print("Debug image saved!")
            
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error converting PDF page from path: {e}")
            return None

    @staticmethod
    def pdf_page_to_base64(pdf_bytes, page=1, size=(600, 800), quality=80):
        """Converts a PDF page to base64-encoded JPEG."""
        try:
            # Open the PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            if page > len(doc):
                return None
            
            # Get the page
            page_obj = doc[page - 1]
            
            # Convert to image
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(size[0]/page_obj.rect.width, size[1]/page_obj.rect.height))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            # img.save(img_byte_arr, format="JPEG", quality=quality)
            
            # Debug: Save image to current directory
            print("Current working directory:", os.getcwd())
            print("Attempting to save debug image...")
            img.save("debug_image.jpg", format="JPEG", quality=quality)
            print("Debug image saved!")
            
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error converting PDF page from bytes: {e}")
            return None

    @staticmethod
    def pdf_page_to_base64_from_url(pdf_url, page=1, size=(600, 800), quality=100):
        """Converts a PDF page from a URL to base64-encoded JPEG."""
        try:
            # Download the PDF from URL
            response = requests.get(pdf_url)
            if response.status_code != 200:
                print(f"Error downloading PDF from URL: HTTP {response.status_code}")
                return None
            
            # Open the PDF from bytes
            doc = fitz.open(stream=response.content, filetype="pdf")
            if page > len(doc):
                return None
            
            # Get the page
            page_obj = doc[page - 1]
            
            # Convert to image
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(size[0]/page_obj.rect.width, size[1]/page_obj.rect.height))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="JPEG", quality=quality)
            
            # Debug: Save image to current directory
            print("Current working directory:", os.getcwd())
            print("Attempting to save debug image...")
            img.save("debug_image.jpg", format="JPEG", quality=quality)
            print("Debug image saved!")
            
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error converting PDF page from URL: {e}")
            return None

    @staticmethod
    def save_image_to_server(img, filename=None):
        """Saves image to server directory and returns the URL."""
        try:
            # Create a unique filename if none provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pdf_page_{timestamp}.jpg"
            
            # Save to server directory (assuming it's in the project root)
            server_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server", "public", "images")
            os.makedirs(server_dir, exist_ok=True)
            
            filepath = os.path.join(server_dir, filename)
            img.save(filepath, format="JPEG", quality=100)
            
            # Return the URL that can be used to access the image
            return f"http://localhost:3000/images/{filename}"
        except Exception as e:
            print(f"Error saving image to server: {e}")
            return None

    @staticmethod
    def pdf_page_to_url_from_path(pdf_path, page=1, size=(600, 800), quality=100):
        """Converts a PDF page from a local path to a URL."""
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            if page > len(doc):
                return None
            
            # Get the page
            page_obj = doc[page - 1]
            
            # Convert to image
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(size[0]/page_obj.rect.width, size[1]/page_obj.rect.height))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save to server and get URL
            return PdfToImage.save_image_to_server(img)
        except Exception as e:
            print(f"Error converting PDF page from path: {e}")
            return None

    @staticmethod
    def pdf_page_to_url_from_url(pdf_url, page=1, size=(600, 800), quality=100):
        """Converts a PDF page from a URL to a URL."""
        try:
            # Download the PDF from URL
            response = requests.get(pdf_url)
            if response.status_code != 200:
                print(f"Error downloading PDF from URL: HTTP {response.status_code}")
                return None
            
            # Open the PDF from bytes
            doc = fitz.open(stream=response.content, filetype="pdf")
            if page > len(doc):
                return None
            
            # Get the page
            page_obj = doc[page - 1]
            
            # Convert to image
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(size[0]/page_obj.rect.width, size[1]/page_obj.rect.height))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save to server and get URL
            return PdfToImage.save_image_to_server(img)
        except Exception as e:
            print(f"Error converting PDF page from URL: {e}")
            return None

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """Extract text from PDF using both PyMuPDF (text extraction) and OCR for images"""
        try:
            # Determine if the path is a URL or a local file path
            if pdf_path.startswith("http"):
                response = requests.get(pdf_path)
                if response.status_code != 200:
                    print(f"Error downloading PDF from URL: HTTP {response.status_code}")
                    return None
                pdf_stream = response.content
            else:
                with open(pdf_path, "rb") as f:
                    pdf_stream = f.read()
            
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            extracted_text = []

            for page in doc:
                # Extract selectable text
                text = page.get_text("text")
                
                # If text is empty, use OCR
                if not text.strip():
                    img = page.get_pixmap()
                    img = Image.frombytes("RGB", [img.width, img.height], img.samples)
                    text = pytesseract.image_to_string(img)
                
                extracted_text.append(text)

            return "\n".join(extracted_text)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
    
    @staticmethod
    def pdf_page_to_text_extracted(pdf_path):
        """Extracts text from a PDF page."""
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            # Initialize an empty string to store the extracted text
            extracted_text = ""

            # Iterate through each page in the PDF
            for page_num in range(len(doc)):
                # Get the page
                page_obj = doc[page_num]
                
                # Extract text from the page
                page_text = page_obj.get_text()
                
                # Append the extracted text to the result string
                extracted_text += page_text + "\n"
            return extracted_text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

