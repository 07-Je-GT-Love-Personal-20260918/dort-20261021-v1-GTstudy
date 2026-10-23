from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re
root=Path('dist')
class Doc(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.links=[];self.reading=0;self.read_depth=0;self.text=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for key in ('href','src'):
   if key in a:self.links.append(a[key])
  if a.get('id')=='reading':self.reading=1
  elif self.reading:self.reading+=1
 def handle_endtag(self,tag):
  if self.reading:self.reading-=1
 def handle_data(self,data):
  if self.reading:self.text.append(data)
docs={p.name:Doc(p.read_text(encoding='utf-8')) for p in root.glob('*.html')}
for name,doc in docs.items():
 assert len(doc.ids)==len(set(doc.ids)),('duplicate',name)
 for link in doc.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  target=u.path or name
  assert (root/unquote(target)).exists(),(name,link)
  if u.fragment and target.endswith('.html'):assert unquote(u.fragment) in docs[target].ids,(name,link)
for name,text in json.loads(Path('cci-creeds.json').read_text(encoding='utf-8')).items():
 assert re.sub(r'\s','',text)==re.sub(r'\s','',''.join(docs[name+'.html'].text)),name
assert len(docs)==8
print(json.dumps({'html_pages':len(docs),'local_links':'pass','unique_ids':'pass','cci_creeds_unchanged':3}))
