from .select import latest
def summarize(builds):
 selected=latest(builds)
 return {'successful_projects':len(selected),'build_ids':[selected[p]['build_id'] for p in sorted(selected)]}
