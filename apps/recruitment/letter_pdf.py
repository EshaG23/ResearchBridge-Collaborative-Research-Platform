"""ResearchBridge's print layout; content comes exclusively from an issued snapshot."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

NAVY=colors.HexColor('#142e39')
TEAL=colors.HexColor('#147965')
MINT=colors.HexColor('#eaf4ef')
INK=colors.HexColor('#263f48')
MUTED=colors.HexColor('#627779')

def render_letter(snapshot):
    fonts=Path(reportlab.__file__).parent/'fonts'
    for name,file in [('RBVera','Vera.ttf'),('RBVeraBold','VeraBd.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    body=ParagraphStyle('body',fontName='RBVera',fontSize=9.5,leading=15,textColor=INK)
    label=ParagraphStyle('label',parent=body,fontName='RBVeraBold',fontSize=7,leading=11,textColor=TEAL,spaceAfter=5)
    value=ParagraphStyle('value',parent=body,fontName='RBVeraBold',fontSize=11,leading=16)
    fine=ParagraphStyle('fine',parent=body,fontSize=7.2,leading=11,textColor=MUTED)
    heading=ParagraphStyle('heading',parent=value,fontSize=14,leading=19,spaceAfter=8)
    p=lambda text,style=body:Paragraph(escape(str(text)),style)
    width=499.28
    def cell(label_text,key,extra=None):
        items=[p(label_text,label),p(snapshot[key],value)]
        if extra:items.extend([Spacer(1,4),p(snapshot[extra],body)])
        return items
    metadata=Table([[p('SELECTION REFERENCE',label),p('ISSUED ON',label)],
        [p(snapshot['reference'],fine),p(snapshot['date'],fine)]],colWidths=[width*.60,width*.40])
    metadata.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),3),('VALIGN',(0,0),(-1,-1),'TOP')]))
    project=Table([[cell('RESEARCH PROJECT','project')],[cell('SELECTED ROLE','role')]],colWidths=[width])
    project.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),MINT),('BOX',(0,0),(-1,-1),.6,colors.HexColor('#cfe3d9')),('LINEBEFORE',(0,0),(0,-1),3,TEAL),('LEFTPADDING',(0,0),(-1,-1),18),('RIGHTPADDING',(0,0),(-1,-1),18),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
    people=Table([[cell('SELECTED STUDENT','student','email'),cell('PROJECT MENTOR','mentor','mentor_email')]],colWidths=[width/2,width/2])
    people.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),18),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    nextbox=Table([[[p('YOUR NEXT STEP',label),p('Begin with trust.',heading),p(snapshot['next_steps'],body)]]],colWidths=[width])
    nextbox.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f1edf7')),('LEFTPADDING',(0,0),(-1,-1),18),('RIGHTPADDING',(0,0),(-1,-1),18),('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),14)]))
    out=BytesIO()
    doc=SimpleDocTemplate(out,pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=225,bottomMargin=56,
        title='ResearchBridge | Offer letter',author='ResearchBridge')
    story=[metadata,Spacer(1,22),p('Dear '+snapshot['student']+','),Spacer(1,9),
        p('You have been selected to join the following research project.'),Spacer(1,18),project,Spacer(1,18),people,Spacer(1,10),nextbox,Spacer(1,18),
        KeepTogether([p('Issued in ResearchBridge by '+snapshot['mentor']+'.',body),Spacer(1,7),p(snapshot['identity'],fine)])]
    def page(canvas,document):
        canvas.saveState()
        canvas.setFillColor(NAVY);canvas.rect(0,641.89,595.28,200,fill=1,stroke=0)
        canvas.saveState()
        clip=canvas.beginPath();clip.rect(0,641.89,595.28,200);canvas.clipPath(clip,stroke=0)
        canvas.setStrokeColor(colors.HexColor('#284650'));canvas.setLineWidth(.8)
        for radius in (48,75,103,131):canvas.circle(557,730,radius,fill=0,stroke=1)
        canvas.restoreState()
        canvas.setFillColor(colors.HexColor('#9dd5bd'));canvas.rect(48,804,25,4,fill=1,stroke=0)
        canvas.setFillColor(colors.white);canvas.setFont('RBVeraBold',12);canvas.drawString(48,780,'RESEARCHBRIDGE')
        canvas.setFillColor(colors.HexColor('#acd6c8'));canvas.setFont('RBVera',7);canvas.drawString(48,763,'RESEARCH  /  COLLABORATION  /  POSSIBILITY')
        canvas.setFillColor(colors.white);canvas.setFont('RBVeraBold',33);canvas.drawString(46,706,'Offer letter')
        canvas.setFont('RBVera',10);canvas.setFillColor(colors.HexColor('#d5e6e4'));canvas.drawString(48,683,'Your next chapter starts with research.')
        canvas.setFillColor(colors.HexColor('#9dd5bd'));canvas.rect(0,638.89,595.28,3,fill=1,stroke=0)
        canvas.setStrokeColor(colors.HexColor('#d6e3dd'));canvas.line(48,43,547,43)
        canvas.setFont('RBVeraBold',7);canvas.setFillColor(TEAL);canvas.drawString(48,28,'RESEARCHBRIDGE')
        canvas.setFont('RBVera',7);canvas.setFillColor(MUTED);canvas.drawString(155,28,'PRIVATE PROJECT SELECTION RECORD')
        canvas.drawRightString(547,28,f'{document.page:02d}')
        canvas.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page)
    return out.getvalue()
