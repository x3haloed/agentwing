#!/usr/bin/env python3
"""AW201 additive native Turbo6 experimental source; no active runtime change."""
import json,re,shutil,subprocess
from pathlib import Path
from run_local_agent import ROOT,digest
BASE=Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo-codebook')
S=BASE.with_name('prism-turbo6');R=Path('/Users/chad/Models/agentwing/evidence/AW-0201')
def main():
 assert not S.exists();R.mkdir(exist_ok=False)
 parent=ROOT/'evidence/AW-0200-value-precision-metal-screen.json';assert json.loads(parent.read_text())['audit']['passed']
 plan={'experiment':'AW-0201','hypothesis':'Additive native6bit100B cache type builds and supports existing256dim Q8/F16key Metal attention paths without altering4bit control','acceptance':'Source reconstruction/diff identities and native library build; correctness/cost/model admission deferred to subsequent screens','parent_sha256':digest(parent),'runner_sha256':digest(Path(__file__)),'source_base':str(BASE),'candidate':str(S),'scope':'Source/build only, not runtime correctness, speed, host/model or endpoint admission'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copytree(BASE,S)
 def edit(name,fn):
  p=S/name;p.write_text(fn(p.read_text()))
 edit('ggml/include/ggml.h',lambda x:x.replace('GGML_TYPE_COUNT   = 147,','GGML_TYPE_TURBO6_0 = 147,\n        GGML_TYPE_COUNT   = 148,'))
 edit('ggml/src/ggml-common.h',lambda x:x.replace('#define QK_TURBO4 128','#define QK_TURBO6 128\ntypedef struct { ggml_half norm; ggml_half rnorm; uint8_t qs[96]; } block_turbo6_0;\nstatic_assert(sizeof(block_turbo6_0)==100,"wrong turbo6 block size");\n\n#define QK_TURBO4 128'))
 for name in ['ggml/src/ggml.c','ggml/src/ggml-quants.h']:
  def transform(x):
   if name.endswith('ggml.c'):
    block=re.search(r'    \[GGML_TYPE_TURBO4_0\] = \{.*?\n    \},',x,re.S)[0];return x.replace(block,block+'\n'+block.replace('TURBO4','TURBO6').replace('turbo4','turbo6'))
   lines=[l for l in x.splitlines() if 'turbo4' in l];return x+'\n#ifdef __cplusplus\nextern "C" {\n#endif\n'+'\n'.join(l.replace('turbo4','turbo6') for l in lines)+'\n#ifdef __cplusplus\n}\n#endif\n'
  edit(name,transform)
 t=json.loads((R.parent/'AW-0199/result.json').read_text())['tables']['6']
 def table(name,values,metal=False):return ('constant' if metal else 'static const')+' float '+name+'['+str(len(values))+']={'+','.join((format(v,'.9g') if v else '0.0')+'f' for v in values)+'};\n'
 ctable=table('centers6',t['centroids'])+table('cuts6',t['thresholds'])
 cpu='''
void quantize_row_turbo6_0_ref(const float * GGML_RESTRICT x, block_turbo6_0 * GGML_RESTRICT y, int64_t count){
 assert(count%128==0);for(int b=0;b<count/128;b++){float n=0,z[128];for(int i=0;i<128;i++)n+=x[b*128+i]*x[b*128+i];n=sqrtf(n);float inv=n>1e-10f?1.f/n:0;for(int i=0;i<128;i++)z[i]=x[b*128+i]*inv;turbo_cpu_fwht(z,128);memset(y+b,0,sizeof(*y));float rn=0;for(int i=0;i<128;i++){int lo=0,hi=63;while(lo<hi){int m=(lo+hi)/2;if(z[i]>=cuts6[m])lo=m+1;else hi=m;}int bit=i*6;for(int k=0;k<6;k++)y[b].qs[(bit+k)/8]|=((lo>>k)&1)<<((bit+k)%8);rn+=centers6[lo]*centers6[lo];}rn=sqrtf(rn);y[b].norm=GGML_FP32_TO_FP16(rn>1e-10f?n/rn:n);}}
void dequantize_row_turbo6_0(const block_turbo6_0 * GGML_RESTRICT x,float * GGML_RESTRICT y,int64_t count){assert(count%128==0);for(int b=0;b<count/128;b++){float scale=GGML_FP16_TO_FP32(x[b].norm);for(int i=0;i<128;i++){int bit=i*6,byte=bit/8,shift=bit%8;unsigned v=x[b].qs[byte];if(shift+6>8)v|=(unsigned)x[b].qs[byte+1]<<8;y[b*128+i]=centers6[(v>>shift)&63]*scale;}}}
size_t quantize_turbo6_0(const float * GGML_RESTRICT src,void * GGML_RESTRICT dst,int64_t nrows,int64_t n_per_row,const float *imatrix){(void)imatrix;quantize_row_turbo6_0_ref(src,dst,nrows*n_per_row);return nrows*n_per_row/128*sizeof(block_turbo6_0);}
'''
 edit('ggml/src/ggml-turbo-quant.c',lambda x:x+'\n'+ctable+cpu)
 metal=table('turbo_centroids_6bit',t['centroids'],True)+table('turbo_mid_6bit',t['thresholds'],True)
 metal+='''
static uint turbo6_index(device const block_turbo6_0 *xb,uint j){uint bit=j*6,byte=bit/8,shift=bit%8;uint v=xb->qs[byte];if(shift+6>8)v|=uint(xb->qs[byte+1])<<8;return (v>>shift)&63;}
template<typename type4x4> void dequantize_turbo6_0(device const block_turbo6_0 *xb,short il,thread type4x4 &reg){float4x4 a;float norm=float(xb->norm);for(int g=0;g<4;g++)for(int k=0;k<4;k++)a[g][k]=turbo_centroids_6bit[turbo6_index(xb,il*16+g*4+k)]*norm;reg=(type4x4)a;}
template<typename type4> void dequantize_turbo6_0_t4(device const block_turbo6_0 *xb,short il,thread type4 &reg){float4 a;float norm=float(xb->norm);for(int k=0;k<4;k++)a[k]=float(half(turbo_centroids_6bit[turbo6_index(xb,il*4+k)]))*norm;reg=type4(a);}
'''
 edit('ggml/src/ggml-metal/kernels/dequantize.h',lambda x:x+'\n'+metal)
 p=S/'ggml/src/ggml-metal/kernels/quantize.metal';x=p.read_text();start=x.index('template<typename TI>\nkernel void kernel_set_rows_turbo4');end=x.index('\n\ntypedef decltype(kernel_set_rows_turbo<int64_t',start);writer=x[start:end].replace('turbo4','turbo6').replace('TURBO4','TURBO6');a=writer.index('        // Step 3:');writer=writer[:a]+'''
        for(int j=0;j<96;j++)blk.qs[j]=0;
        float rn=0;uint ids[128];for(int j=0;j<128;j++){uint lo=0,hi=63;while(lo<hi){uint m=(lo+hi)/2;if(x[j]>=turbo_mid_6bit[m])lo=m+1;else hi=m;}ids[j]=lo;float c=turbo_centroids_6bit[lo];rn+=c*c;}
        for(int j=0;j<32;j++){uint v=ids[4*j]|(ids[4*j+1]<<6)|(ids[4*j+2]<<12)|(ids[4*j+3]<<18);blk.qs[3*j]=uchar(v);blk.qs[3*j+1]=uchar(v>>8);blk.qs[3*j+2]=uchar(v>>16);}
        blk.rnorm=half(0);rn=sqrt(rn);blk.norm=half(rn>1e-10f?grp_norm/rn:grp_norm);
    }
}
''';p.write_text(x+'\n'+writer+'\ntypedef decltype(kernel_set_rows_turbo6<int64_t>) set_rows_turbo6_t;\ntemplate [[host_name("kernel_set_rows_f32_i64_turbo6")]] kernel set_rows_turbo6_t kernel_set_rows_turbo6<int64_t>;\ntemplate [[host_name("kernel_set_rows_f32_i32_turbo6")]] kernel set_rows_turbo6_t kernel_set_rows_turbo6<int32_t>;\n')
 edit('ggml/src/ggml-metal/kernels/fa.metal',lambda x:''.join(l+(l.replace('turbo4','turbo6') if 'template [[host_name(' in l and 'turbo4' in l else '') for l in x.splitlines(True)))
 for name in ['ggml/src/ggml-metal/ggml-metal-device.m','ggml/src/ggml-metal/ggml-metal-ops.cpp','src/llama-context.cpp','src/llama-graph.cpp','common/arg.cpp']:
  def guards(x):
   x=re.sub(r'([\w>\.\[\]-]+) == GGML_TYPE_TURBO4_0',r'(\1 == GGML_TYPE_TURBO4_0 || \1 == GGML_TYPE_TURBO6_0)',x)
   x=x.replace('case GGML_TYPE_TURBO4_0:', 'case GGML_TYPE_TURBO4_0:\n                    case GGML_TYPE_TURBO6_0:')
   if name=='common/arg.cpp':x=x.replace('    GGML_TYPE_TURBO4_0,','    GGML_TYPE_TURBO4_0,\n    GGML_TYPE_TURBO6_0,')
   return x
  edit(name,guards)
 changed=[]
 for p in S.rglob('*'):
  if p.is_file() and digest(p)!=digest(BASE/p.relative_to(S)):changed.append({'path':str(p.relative_to(S)),'before':digest(BASE/p.relative_to(S)),'after':digest(p)})
 (R/'source-changes.json').write_text(json.dumps(changed,indent=2)+'\n');print(json.dumps(changed,indent=2))
if __name__=='__main__':main()
