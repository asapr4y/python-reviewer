import sys,re,json,hashlib,shutil
from pathlib import Path
from collections import Counter
sys.path.insert(0,'.tools')
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'public'/'assets'; ASSETS.mkdir(parents=True,exist_ok=True)
clean=lambda s:s.replace('\u200b','').strip()
allq=[]
for si,name in enumerate(['Python Programming.pdf','Python Programming.docx.pdf'],1):
 doc=fitz.open(Path('C:/Users/Ray/Downloads')/name)
 shutil.copyfile(Path('C:/Users/Ray/Downloads')/name,ROOT/'public'/'sources'/f'source-{si}.pdf')
 current=None; mode='body'; imgnum=0
 for pi,p in enumerate(doc):
  items=[]
  for b in p.get_text('dict')['blocks']:
   if b['type']==0:
    for line in b['lines']:
     text=clean(''.join(s['text'] for s in line['spans']))
     if not text:continue
     rect=fitz.Rect(line['bbox'])*p.rotation_matrix
     items.append({'kind':'text','text':text,'x':rect.x0,'y':rect.y0,'page':pi+1,'h':rect.height})
   elif b['type']==1:
    # Repeated site logo is furniture, retained in original PDF.
    if si==1 and abs(b['bbox'][2]-b['bbox'][0]-59.28)<1:continue
    if b['width']<15 and b['height']<15:
     for prev in items:
      if prev['kind']=='text' and abs(prev['y']-(fitz.Rect(b['bbox'])*p.rotation_matrix).y0)<5:
       prev['text']='\u2022 '+prev['text']
     continue
    imgnum+=1; path=f'assets/s{si}-p{pi+1}-i{imgnum}.png'
    pix=fitz.Pixmap(b['image'])
    if pix.n>4:pix=fitz.Pixmap(fitz.csRGB,pix)
    pix.save(str(ROOT/'public'/path))
    rect=fitz.Rect(b['bbox'])*p.rotation_matrix
    items.append({'kind':'image','src':path,'width':pix.width,'height':pix.height,'x':rect.x0,'y':rect.y0,'page':pi+1})
  items.sort(key=lambda a:(round(a['y']/3)*3,a['x']))
  for item in items:
   t=item.get('text','')
   num=re.fullmatch(r'QUESTION (\d+)',t) if si==1 else (re.fullmatch(r'(\d+)\.?',t) if item['kind']=='text' and item['x']<45 else None)
   if si==2 and pi==7 and t=='You write the following code:' and current and current['number']==21:
    num=re.match(r'(22)','22')
   if num:
    n=int(num[1]); current={'id':f's{si}-q{n}','source':si,'number':n,'page':pi+1,'body':[],'key':[],'notes':[]};allq.append(current);mode='body';continue
   if not current:continue
   if 'https://www.gratisexam.com/' in t or t=='Exam A':continue
   if si==1 and t.startswith('Correct Answer:'):
    mode='key';current['keyText']=t;continue
   if si==1 and t.startswith('Section:'):mode='notes';continue
   if si==2 and re.match(r'^(Ans[.:]|Answer:)',t):
    current['key'].append(item);continue
   # Q47's explicit result key, without an Ans prefix.
   if si==2 and current['number']==47 and re.fullmatch(r'[ABC] [–-] [23]',t):
    current['key'].append(item);continue
   current[mode].append(item)
# Explicit keys transcribed from the highlighted/printed answers. They are not corrected.
mc1={3:'B',9:'B',11:'C',12:'BE',13:'CE',14:'C',15:'BC',17:'A',18:'B',19:'C',21:'FGH',22:'A'}
mc2={1:'C',2:'A',3:'D',4:'C',5:'A',6:'A',7:'D',8:'C',9:'D',10:'C',11:'B',12:'B',13:'B',14:'B',15:'A',16:'D',17:'C',24:'C',25:'C',26:'CD',27:'AF',28:'AB',29:'CE',30:'BC',31:'AB',32:'FGH',33:'ACE'}
custom={}
def slots(si,n,answers,choices,labels=None,ordered=False):
 custom[(si,n)]={'type':'slots','answers':answers,'slotChoices':choices,'labels':labels or [f'Position {i+1}' for i in range(len(answers))],'ordered':ordered}
slots(1,1,['3','6','5','1'],[['1','2','3','4','5','6']]*4,ordered=True)
slots(1,2,['b*c','addition','(a + (b*c)) - d'],[['a+b','b*c','c-d'],['addition','subtraction'],['(a+b) * (c-d)','(a + (b*c)) - d','a + ((b*c) - d)']],['Which part of the expression will be evaluated first?','Which operation will be evaluated second?','Which expression is equivalent to the expression in the function?'])
slots(1,4,['int and string','string','Invalid syntax'],[['bool and string','float and bool','int and string','float and int'],['bool','float','int','string'],['Invalid syntax','Mismatched data type(s)','Misnamed variable(s)']],['Which two data types are stored in the rooms list at line 01?','What is the data type of room at line 02?','Why does line 03 fail to find the rooms?'])
slots(1,5,['float','float','str','bool'],[['int','float','str','bool']]*4,['type (+1E10)','type (5.0)','type ("True")','type (False)'])
slots(1,6,['word in word_list:','letter in word:'],[['word_list in word:','word in word_list:','word == word_list:','word is word_list:'],['word is letter:','letter is word:','word in letter:','letter in word:']],['for','if'])
ops=['And','Addition and Subtraction','Multiplication and Division','Exponents','Parenthesis','Unary positive, negative, not']
slots(1,7,[ops[i] for i in [4,3,5,2,1,0]],[ops]*6,ordered=True)
slots(1,8,['int','bool','str','float','str'],[['bool','float','int','str']]*5,['age = 2','minor = False','name = "Contoso"','weight = 123.5','zip = "81000"'])
slots(1,10,['(','-','a',')','**2'],[['-','(',')','**','**2','2','a']]*5,ordered=True)
files=["with open(filename, 'r') as file:",'if os.path.isfile(filename):','return file.readline()','else:','return None']
slots(1,16,files,[files]*5,ordered=True)
slots(1,20,['while (index < 10):','if numbers[index] == 6:'],[['while (index < 10):','while (index < 10)','while (index < 5):','while (index < 5)'],['if numbers[index] = 6','if numbers[index] == 6:','if numbers[index] > 6:','if numbers[index] != 6']],['Line 03','Line 06'])
letterSlots={18:('BAB','ABC'),19:('CDB','ABCD'),20:('AB','ABCD'),21:('BAB','ABC'),22:('ABA','ABC'),23:('ABCD','ABCD'),34:('AGCE','ABCDEFG'),41:('FDEB','ABCDEF'),42:('EDFCBA','ABCDEF'),43:('CDABE','ABCDE'),44:('EACDB','ABCDE'),45:('BAGCE','ABCDEFG'),46:('AGFE','ABCDEFG'),48:('BBCD','ABCD'),49:('ADCBC','ABCD'),50:('CFHBHA','ABCDEFGH'),51:('CBAA','ABCD'),52:('ACE','ABCDEFG'),53:('BDDD','ABCD'),54:('BAAB','AB')}
for n,(ans,opts) in letterSlots.items():slots(2,n,list(ans),[list(opts)]*len(ans),ordered=n in [34,41,42,43,44,45,46])
custom[(2,18)]['slotChoices']=[list('ABC'),list('AB'),list('ABC')]
custom[(2,19)]['slotChoices']=[list('ABCD'),list('ABCD'),list('ABC')]
custom[(2,21)]['slotChoices']=[list('ABCD')]*3
slots(2,47,['2','2','3'],[['2','3']]*3,['A','B','C'])
for n,ans in {35:['No','No','Yes','Yes'],36:['Yes','No','No'],37:['Yes','No','No','No'],38:['Yes','Yes','Yes','No'],39:['Yes','Yes','No','No'],40:['Yes','No','Yes','Yes']}.items():
 slots(2,n,ans,[['Yes','No']]*len(ans),[f'Statement {i+1}' for i in range(len(ans))])
for q in allq:
 original_body_text=' '.join(b.get('text','') for b in q['body'])
 si=q['source'];n=q['number'];q['title']=next((i['text'] for i in q['body'] if i['kind']=='text' and len(i['text'])>35),'Question '+str(n))
 if (si,n) in custom:q.update(custom[(si,n)])
 else:
  ans=(mc1 if si==1 else mc2)[n];q.update(type='multi' if len(ans)>1 else 'single',answers=list(ans))
  # Gather the exact choice wording, retaining code images where applicable.
  body=[];options=[];active=None
  for item in q['body']:
   match=re.match(r'^([A-H])\.\s*(.*)',item.get('text',''))
   if match:
    active={'value':match[1],'text':match[2],'parts':[]};options.append(active)
   elif active:
    if item['kind']=='text':active['text']+='\n'+item['text']
    else:active['parts'].append(item)
   else:body.append(item)
  q['body']=body;q['options']=options
  if si==2 and n==7:
   q['options']=[{'value':v,'text':text,'parts':[]} for v,text in zip('ABCD',[
    '05 if line != \u2018\u2018:\n06    if line !=\u201d\u201d:',
    '05 if line != \u2018\\n\u2019:\n06    if line != None:',
    '05 if line != \u2018\\n\u2019:\n06    if line != \u201c\u201d:',
    '05 if line != \u2018\u2018:\n06    if line != \u201c\\n\u201d:'])]
 # Preserve table statements as rows and put response controls beside them.
 if si==2 and 35<=n<=40:
  statements={
   35:['What is displayed after the first print?','What is displayed after the second print?','What is displayed after the third print?','What is displayed after the fourth print?'],
   36:['After executing code segment 1, the data type of variable a is str.','After executing code segment 2, the data type of variable b is float.','After executing code segment 3, the data type of variable c is int.'],
   37:['Lines 01 through 04 will be ignored for syntax checking.','The pound sign (#) is optional for lines 02 and 03.','The string in line 06 will be interpreted as a comment.','Line 07 contains an inline comment.'],
   38:['A try statement can have one or more except clauses.','A try statement can have a finally clause without an except clause.','A try statement can have a finally clause and an except clause.','A try statement can have one or more finally clauses.'],
   39:['To meet the requirements, line 01 must be changed to the following: def increnient_score(score, bonus, points = 1):','Once any parameter is defined with a default value, any parameters to the right must also be defined with default values.','If the function is called with only two parameters, the value of the third parameter will be None.','Line 03 will also modify the value of the variable points declared at line 06.'],
   40:['The print statement at line 04 will only print if the two numbers are equal in value.','The print statement at line 06 will only print if num1 is less than num2.','The print statement at line 08 will only print if num1 is greater than num2.','The statement at line 09 is an invalid comparison.']
  }[n]
  q['labels']=statements;q['statements']=statements
  stop=next((i for i,b in enumerate(q['body']) if b.get('text')=='Yes'),None)
  if stop is not None:q['body']=q['body'][:stop]

 # Keep choices printed side by side on a single readable row.
 if si==2 and q['type']=='slots':
  rows=[]
  for item in q['body']:
   if rows and item['kind']=='text' and rows[-1]['kind']=='text' and item['page']==rows[-1]['page'] and abs(item['y']-rows[-1]['y'])<3:
    rows[-1]['text']+='    '+item['text'];rows[-1]['tableRow']=True
   else:rows.append(item)
  q['body']=rows
 # Make question text readable without changing words, code, or ordering.
 for field in ['body','notes','key']:
  blocks=[]
  for item in q[field]:
   if item['kind']=='text' and not item['text']:continue
   if blocks and item['kind']=='text' and blocks[-1]['kind']=='text':
    prev=blocks[-1]
    # Merge lines only when they are a continuous paragraph in the same column.
    gap=item['y']-prev.get('lastY',prev['y']);iscode=bool(re.match(r'^(\d{2}\b|[\[A-H].*[\]}.]|[A-H]\. |Ans[.:]|Answer:)',item['text']))
    if not re.match(r'^[a-zA-Z_]+\s*=',item['text']) and not re.match(r'^[a-zA-Z_]+\s*=',prev['text']) and item['page']==prev['page'] and 0<gap<18 and abs(item['x']-prev['x'])<3 and not iscode and not prev.get('code') and not prev.get('tableRow') and not item.get('tableRow') and not re.match(r'^(Which|How|You |What |For |NOTE:|To |The code|Each |A float|The function|Any decimal|\u2022 |\.)',item['text']):
     prev['text']+=' '+item['text'];prev['lastY']=item['y'];continue
   blocks.append({**item,'code':bool(re.match(r'^\d{2}\b',item.get('text','')))})
  q[field]=blocks
 if q['type']=='slots' and si==1 and n==1:q['responseHint']='Use the code segments from top to bottom as 1–6. Select four in the requested order.'
 elif q['type']=='slots':q['responseHint']='Select an answer for each position in the order shown in the source.'
 q['searchText']=' '.join(b.get('text','') for b in q['body'])+' '+' '.join(o.get('text','') for o in q.get('options',[]))+' '+' '.join(q.get('statements',[]))
 ignore=set('ABCDEFGH')|{'Yes','No','〇'}
 tokens=lambda t:Counter(w for w in re.findall(r'\w+',t) if w not in ignore)
 missing=tokens(original_body_text)-tokens(q['searchText'])
 assert not missing,(q['id'],'Missing source text:',missing)
assert len(allq)==76,(len(allq),[(q['source'],q['number']) for q in allq])
for q in allq:
 assert q['answers'] and q['body'],q['id']
 if q['type']!='slots':assert set(q['answers'])<={o['value'] for o in q['options']},q['id']
(ROOT/'public'/'questions.json').write_text(json.dumps({'sources':[{'id':1,'name':'Python Programming.pdf','short':'Exam A','count':22,'pages':36,'file':'sources/source-1.pdf'},{'id':2,'name':'Python Programming.docx.pdf','short':'Practice set','count':54,'pages':23,'file':'sources/source-2.pdf'}],'questions':allq},ensure_ascii=False,indent=2),encoding='utf8')
print('Extracted',len(allq),'questions with',sum(len(q['answers']) for q in allq),'answer selections.')
for q in allq:print(q['id'],q['type'],','.join(q['answers']),len(q['body']),'blocks',len(q.get('options',[])),'options')
