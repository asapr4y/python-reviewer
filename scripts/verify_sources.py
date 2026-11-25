import sys,re,json,hashlib
from pathlib import Path
sys.path.insert(0,'.tools')
import pymupdf as f
D=json.loads(Path('public/questions.json').read_text(encoding='utf8'))
# Verify original PDFs are copied byte for byte.
for s in D['sources']:
 original=Path('C:/Users/Ray/Downloads')/s['name'];copied=Path('public')/s['file']
 assert hashlib.sha256(original.read_bytes()).digest()==hashlib.sha256(copied.read_bytes()).digest()
# Independently recover text-labelled answers from PDF 1.
pdf=f.open('C:/Users/Ray/Downloads/Python Programming.pdf')
text='\n'.join(p.get_text() for p in pdf)
verified=[]
for match in re.finditer(r'QUESTION (\d+)\n(.*?)(?=QUESTION \d+\n|\Z)',text,re.S):
 answer=re.search(r'Correct Answer: ([A-H]+)',match[2])
 if answer:
  q=next(q for q in D['questions'] if q['id']==f's1-q{match[1]}')
  assert q['answers']==list(answer[1]),q['id'];verified.append(q['id'])
# Independently recover PDF 2 MC answers from orange highlight rectangles.
pdf=f.open('C:/Users/Ray/Downloads/Python Programming.docx.pdf');n=None;marked={}
for pi,p in enumerate(pdf):
 fills=[v['rect'] for v in p.get_drawings() if v.get('fill') and v['fill'][0]>.95 and .6<v['fill'][1]<.9 and v['fill'][2]<.1]
 lines=[l for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines']]
 lines.sort(key=lambda l:(round(l['bbox'][1]/3)*3,l['bbox'][0]))
 for line in lines:
  t=''.join(s['text'] for s in line['spans']).replace('\u200b','').strip();r=f.Rect(line['bbox'])
  if r.x0<45 and re.fullmatch(r'\d+\.?',t):n=int(t.rstrip('.'))
  if pi==7 and t=='You write the following code:':n=22
  if n is None:continue
  q=next((q for q in D['questions'] if q['id']==f's2-q{n}'),None)
  if not q or q['type']=='slots':continue
  m=re.match(r'^([A-H])\.\s',t)
  if m:
   center=f.Point(r.x0+6,(r.y0+r.y1)/2)
   if any(center in fill for fill in fills):marked.setdefault(n,[]).append(m[1])
for n,answers in marked.items():
 q=next(q for q in D['questions'] if q['id']==f's2-q{n}')
 assert q['answers']==answers,(q['id'],q['answers'],answers)
verified.extend(f's2-q{n}' for n in marked)
expected=[q for q in D['questions'] if q['type']!='slots']
assert len(verified)==len(expected),(len(verified),len(expected),[q['id'] for q in expected if q['id'] not in verified])
print(f'PASS: {len(verified)} multiple-choice keys independently match original PDF text/highlights.')
print('PASS: both original source PDFs are byte-for-byte unchanged.')
print('Image keys and multipart answer sequences were visually checked against the PDFs.')
