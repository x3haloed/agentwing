from .select import latest
def summarize(builds):
 selected={p:b for p,b in latest(builds).items() if b['status']=='success'}
 return {'successful_projects':len(selected),'build_ids':[selected[p]['build_id'] for p in sorted(selected)]}
