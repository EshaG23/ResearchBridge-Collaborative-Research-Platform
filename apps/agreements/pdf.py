from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Flowable,KeepTogether

class Signature(Flowable):
    width=487
    height=150
    def __init__(self,strokes,name,method):
        super().__init__();self.width=487;self.height=150;self.strokes=strokes;self.name=name;self.method=method
    def draw(self):
        c=self.canv;c.setFillColor(colors.HexColor('#edf5f1'));c.roundRect(0,0,self.width,self.height,8,fill=1,stroke=0)
        c.setStrokeColor(colors.HexColor('#1b4050'));c.setLineWidth(1.7)
        if self.method=='drawn':
            for stroke in self.strokes:
                if len(stroke)<2:continue
                path=c.beginPath();path.moveTo(15+stroke[0][0]*457,12+(1-stroke[0][1])*125.675)
                for x,y in stroke[1:]:path.lineTo(15+x*457,12+(1-y)*125.675)
                c.drawPath(path)
        else:
            c.setFillColor(colors.HexColor('#1b4050'));font=20
            while pdfmetrics.stringWidth(self.name,'NDAItalic',font)>455 and font>7:font-=1
            c.setFont('NDAItalic',font);c.drawString(16,45,self.name if self.method=='typed' else 'Physical signature: see attached signed copy')

def agreement_pdf(snapshot,evidence=None):
    root=Path(reportlab.__file__).parent/'fonts'
    for name,file in [('NDA','Vera.ttf'),('NDABold','VeraBd.ttf'),('NDAItalic','VeraIt.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,str(root/file)))
    body=ParagraphStyle('body',fontName='NDA',fontSize=9,leading=14,textColor=colors.HexColor('#263f48'),spaceAfter=10)
    heading=ParagraphStyle('head',parent=body,fontName='NDABold',fontSize=12,leading=16,spaceBefore=8,spaceAfter=7)
    small=ParagraphStyle('small',parent=body,fontSize=7,leading=10,textColor=colors.HexColor('#657779'))
    p=lambda text,style=body:Paragraph(escape(str(text)),style)
    template=snapshot['template'];out=BytesIO()
    doc=SimpleDocTemplate(out,pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=145,bottomMargin=55,title=template['title'],author='ResearchBridge')
    story=[p(template['notice'],small),p('Project: '+snapshot['project'],heading),p('Student: '+snapshot['student']+' | '+snapshot['email']),p('Template: '+template['version']+' | Reference: '+snapshot['reference'],small)]
    for title,text in template['clauses']:story.append(KeepTogether([p(title,heading),p(text)]))
    story.extend([PageBreak(),p('Signature and completion record',heading),p('Project: '+snapshot['project']),p('Student: '+snapshot['student']+' | '+snapshot['email']),p('Agreement reference: '+snapshot['reference'],small),p('Template fingerprint: '+snapshot['template_hash'],small),p(template['consent']),Spacer(1,10)])
    if evidence:
        story.extend([Signature(evidence['signature'],evidence['name'],evidence['method']),Spacer(1,12),p('Signed name: '+evidence['name']),p('Method: '+evidence['method']),p('Submitted at: '+evidence['date']),p('Evidence reference: '+evidence['id'],small),p('Account password confirmed before submission. Mentor verification is recorded separately in the private agreement history.',small),p('This record captures an electronic signature or physical-copy submission. It does not contain a certificate-backed digital signature.',small)])
    else:
        story.extend([Spacer(1,30),p('Signature: __________________________________________________'),Spacer(1,20),p('Full name: _________________________________________________'),Spacer(1,20),p('Date: _____________________________________________________'),p('Sign this complete agreement and upload all pages. The mentor must verify the submitted copy.',small)])
    def page(c,d):
        c.saveState();c.setFillColor(colors.HexColor('#142e39'));c.rect(0,723,596,119,fill=1,stroke=0)
        c.setFont('NDABold',12);c.setFillColor(colors.white);c.drawString(48,799,'RESEARCHBRIDGE')
        c.setFont('NDABold',23);c.drawString(48,762,'Confidentiality agreement')
        c.setFont('NDA',8);c.setFillColor(colors.HexColor('#a7d5c4'));c.drawString(48,741,'SAMPLE DEVELOPMENT TEMPLATE' if template['sample'] else 'PROJECT AGREEMENT')
        c.setStrokeColor(colors.HexColor('#b9d5c9'));c.line(48,39,547,39)
        c.setFont('NDA',7);c.setFillColor(colors.HexColor('#657779'));c.drawString(48,25,'PRIVATE AGREEMENT RECORD | '+template['version']);c.drawRightString(547,25,str(d.page));c.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page)
    return out.getvalue()
