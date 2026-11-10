"""Printable companion to the accessible HTML timetable."""
def schedule_pdf(days):
    commands=[]
    def text(x,y,value,size=11,bold=False,color='0.12 0.12 0.14'):
        escaped=value.replace('–','-').replace('—','-').replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
        commands.append(f'BT /F{2 if bold else 1} {size} Tf {color} rg 1 0 0 1 {x} {y} Tm ({escaped}) Tj ET')
    def rect(x,y,w,h,color):
        commands.append(f'{color} rg {x} {y} {w} {h} re f')
    text(44,792,'JD Dance',26,True)
    text(44,766,'Weekly class schedule',16,True)
    text(44,741,'Lockett St, Manchester M8 8EF',10)
    text(44,725,'jddanceex@gmail.com  |  07587 107 317  |  jddance.info',10)
    for i,item in enumerate(days):
        day=item["day"]
        y=685-i*110
        rect(40,y-5,515,25,'0.88 0.96 0.86')
        text(50,y+3,day,12,True)
        text(255,y+3,'Time',10,True)
        text(420,y+3,'Age',10,True)
        text(500,y+3,'Price',10,True)
        rows=[(c['name'],c['details'],c['price'],c.get('age')) for c in item['classes']]
        for j,(name,time,price,age) in enumerate(rows):
            row_y=y-27-j*23
            text(50,row_y,name)
            text(255,row_y,time)
            if age:
                text(420,row_y,'Age '+age,10,True,'0.65 0.12 0.38')
            text(500,row_y,price,11,True)
    text(44,110,'Payments can be made weekly or monthly.',10)
    rect(40,53,515,35,'1 0.91 0.96')
    text(50,66,'Class enquiries: contact us for availability or help choosing a class.',10)
    stream='\n'.join(commands).encode('cp1252')
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream']
    pdf=bytearray(b'%PDF-1.4\n'); offsets=[0]
    for i,obj in enumerate(objects,1):
     offsets.append(len(pdf)); pdf.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref=len(pdf)
    pdf.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:pdf.extend(f'{offset:010d} 00000 n \n'.encode())
    pdf.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(pdf)
