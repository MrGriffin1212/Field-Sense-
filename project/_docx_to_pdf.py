from docx2pdf import convert
src = r"C:\Users\saket\project\FieldSense_Report.docx"
dst = r"C:\Users\saket\project\FieldSense_Report.pdf"
convert(src, dst)
print("PDF:", dst)
