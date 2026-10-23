import json, sys, requests
BASE='http://127.0.0.1:8000'
passed=0; total=0
def check(name, fn):
 global passed,total
 total+=1
 try:
  ok=fn(); print(('PASS' if ok else 'FAIL'),name); passed+=bool(ok)
 except Exception as e: print('FAIL',name,e)
check('health',lambda: requests.get(BASE+'/health',timeout=5).status_code==200)
check('sources',lambda: len(requests.get(BASE+'/sources',timeout=5).json()['sources'])>=4)
check('general answer',lambda: requests.post(BASE+'/ask',json={'question':'What does the placement policy say about PPO reporting?'},timeout=5).json()['answer_type']=='retrieved_fact')
check('personal refusal',lambda: requests.post(BASE+'/ask',json={'question':'What is my placement eligibility?'},timeout=5).json()['answer_type']=='refused')
r=requests.post(BASE+'/ask',headers={'X-Student-Id':'S1001'},json={'question':'What is my placement eligibility?'},timeout=5)
check('personal calculation',lambda: r.json()['answer_type']=='calculated' and bool(r.json()['tools_invoked']))
check('audit',lambda: requests.get(BASE+'/audit/'+r.json()['trace_id'],timeout=5).status_code==200)
meta={'doc_id':'SMOKE-UPLOAD','title':'Smoke test document','issuer':'Test issuer','authority_level':3,'doc_type':'notice','version':'1','effective_from':'2026-01-01','effective_to':'','supersedes':'','scope_programmes':'ALL','scope_batches':'ALL','provenance':'Automated smoke test','retrieved_on':'2026-10-23','synthetic':'N'}
check('live ingestion',lambda: requests.post(BASE+'/ingest',files={'file':('smoke.txt',b'authorized smoke-test text','text/plain')},data={'metadata':json.dumps(meta)},timeout=5).status_code==200)
print(f'{passed}/{total} checks passed')
sys.exit(0 if passed==total else 1)
