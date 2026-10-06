#!/usr/bin/env python3
"""AW184 analytical Gaussian scalar quantizer screen; no codec/runtime edits."""
import json,math,re,statistics,subprocess
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0184')
S=Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo-mixed-graph')
SIGMA=1/math.sqrt(128)
def phi(z):return math.exp(-z*z/2)/math.sqrt(2*math.pi) if math.isfinite(z) else 0.
def cdf(z):return .5*math.erfc(-z/math.sqrt(2))
def moments(a,b):
 a/=SIGMA;b/=SIGMA;p=cdf(b)-cdf(a);m=SIGMA*(phi(a)-phi(b));s=SIGMA**2*(p+(a*phi(a) if math.isfinite(a) else 0)-(b*phi(b) if math.isfinite(b) else 0));return p,m,s
def evaluate(cuts,centers):
 bounds=[-math.inf]+list(cuts)+[math.inf];means=[];mse=0.
 for i,c in enumerate(centers):
  p,m,s=moments(bounds[i],bounds[i+1]);means.append(m/p);mse+=s-2*c*m+c*c*p
 return mse,np.array(means)
def quadrature(cuts,centers):
 x=np.linspace(-8*SIGMA,8*SIGMA,1000001);y=np.array(centers)[np.searchsorted(cuts,x,side='right')];density=np.exp(-.5*(x/SIGMA)**2)/(SIGMA*math.sqrt(2*math.pi));return float(np.trapezoid((x-y)**2*density,x))
def main():
 R.mkdir(exist_ok=False);source=S/'ggml/src/ggml-metal/kernels/dequantize.h';text=source.read_text()
 def table(name):
  m=re.search(r'constant float '+name+r'\[\d+\]\s*=\s*\{([^}]+)\}',text);assert m;return np.array([float(x.strip().removesuffix('f')) for x in m[1].split(',') if x.strip()])
 old=table('turbo_centroids_4bit');cuts=table('turbo_mid_4bit');assert len(old)==16 and len(cuts)==15 and np.all(np.diff(old)>0)
 plan={'experiment':'AW-0184','hypothesis':'Published native16centroid table satisfies Lloyd centroid fixed-point condition for Gaussian variance1/128 at nearest-cell boundaries','primary_metric':'Analytic conditional-mean residual and Gaussian scalar MSE, independently quadrature checked; no vector norm-correction/model-quality inference','acceptance':'Fixed-point maxcentroid residual<=1e-6 allows six-decimal rounding; quadrature relative agreement<=1e-5. Alternative stationary table only a mathematical survivor, not production acceptance','sigma':SIGMA,'old_centroids':old.tolist(),'old_thresholds':cuts.tolist(),'source_sha256':digest(source),'runner_sha256':digest(Path(__file__)),'parent_receipt_sha256':digest(ROOT/'evidence/AW-0183-graph-mixed-cache-terminal.json'),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'scope':'Analytical Gaussian proxy without raw model data, inference, tool calls, or speed claims'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');baseline=host_sample();mse,conditional=evaluate(cuts,old);candidate=old.copy()
 for iteration in range(50000):
  thresholds=(candidate[:-1]+candidate[1:])/2;_,updated=evaluate(thresholds,candidate);change=float(np.max(np.abs(updated-candidate)));candidate=updated
  if change<1e-13:break
 else:raise RuntimeError('No convergence')
 thresholds=(candidate[:-1]+candidate[1:])/2;cmse,means=evaluate(thresholds,candidate);qold=quadrature(cuts,old);qnew=quadrature(thresholds,candidate);assert abs(qold-mse)/mse<=1e-5 and abs(qnew-cmse)/cmse<=1e-5
 assert np.allclose(candidate,-candidate[::-1],atol=1e-12) and np.max(np.abs(means-candidate))<1e-12
 after=host_sample();check_sample(after,baseline[1]);result={'experiment':'AW-0184','native_fixed_point_passed':bool(np.max(np.abs(conditional-old))<=1e-6),'native_max_centroid_residual':float(np.max(np.abs(conditional-old))),'native_conditional_means':conditional.tolist(),'native_gaussian_mse':mse,'candidate_gaussian_mse':cmse,'candidate_centroids':candidate.tolist(),'candidate_thresholds':thresholds.tolist(),'candidate_fixed_point_max_residual':float(np.max(np.abs(means-candidate))),'convergence_iterations':iteration+1,'relative_mse_reduction':1-cmse/mse,'quadrature_mse':{'native':qold,'candidate':qnew},'phase_host_samples':[baseline,after],'plan_sha256':digest(R/'plan.json'),'disposition':'Retain analytical alternative only; actual norm-corrected vector/nativeGPU/own-model/vision/tools/endpoints remain required','scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
