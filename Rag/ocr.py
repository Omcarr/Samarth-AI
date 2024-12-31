import pytesseract
from pdf2image import convert_from_path


def extract_text(pdf_file_path:str):
    
    pages = convert_from_path(pdf_file_path)

    text = ""
    for page in pages:
    #   display(page)
        text += pytesseract.image_to_string(page) + "\n"
        # print(text)
    
    return text

if __name__ == "__main__":
    extract_text("Types_of_Arrhythmia_Detection_using_ML.pdf")

# import pymupdf


# def extract_text_from_pdf(pdf_file_path):
#     # Open the PDF file
#     document = pymupdf.open(pdf_file_path)

#     text = ""
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)  # Get each page
#         text += page.get_text()  # Extract text from the page

#     return text

# # text = extract_text_from_pdf("Types_of_Arrhythmia_Detection_using_ML.pdf")

# # print(text)
