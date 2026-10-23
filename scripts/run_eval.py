import json,time,statistics,requests
from pathlib import Path
base='http://127.0.0.1:8000'; cases=json.loads(Path('data/evaluation_set.json').read_text()); results=[]
for i,c in enumerate(cases,1):
 t=time.perf_counter(); h={'X-Student-Id':c['student_id']} if c.get('student_id') else {}; r=requests.post(base+'/ask',headers=h,json={'question':c['question']},timeout=20); ms=(time.perf_counter()-t)*1000
 body=r.json(); results.append({'id':i,'question':c['question'],'expected':c['answer_type'],'actual':body.get('answer_type'),'correct':body.get('answer_type')==c['answer_type'],'latency_ms':round(ms,2),'trace_id':body.get('trace_id')})
Path('reports/evaluation_results.json').write_text(json.dumps(results,indent=2))
correct=sum(x['correct'] for x in results); lat=[x['latency_ms'] for x in results]
report=f'''# Evaluation report\n\nRun date: 2026-10-23. Environment: local Sandbox API on localhost, lexical retrieval, mock explanation mode.\n\nCases: {len(results)}\nAnswer-type exact matches: {correct}/{len(results)} ({correct/len(results):.1%})\nLatency p50: {statistics.median(lat):.2f} ms\nLatency p95: {sorted(lat)[max(0,int(len(lat)*.95)-1)]:.2f} ms\n\nThese are measured demo results, not production performance claims. The evaluation is primarily a contract smoke evaluation; prose correctness and citation accuracy require human review.\n\nKnown limitation: two real DTU source documents are present instead of the requested three.\n'''
Path('reports/evaluation_report.md').write_text(report)
print(report)
