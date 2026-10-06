#include <metal_stdlib>
using namespace metal;
struct Block { uchar qs[24];uchar qh[2];half d; };
struct Args {uint blocks;uint rows;};
inline float dot_reg(device const Block &v,thread const float *c,float sy,uint it) {
 float acc=0; const float powers[5]={3,9,27,81,243};
 #pragma unroll
 for(uint k=0;k<3;k++) {
  uint code=v.qs[k<2?2*it+k:16+it];
  #pragma unroll
  for(uint j=0;j<5;j++)acc+=floor(powers[j]*(float(code)/256.0f))*c[k*5+j];
 }
 float u=float(v.qh[it&1])/256.0f,p=it<2?1.0f:it<4?3.0f:it<6?9.0f:27.0f;
 acc+=(floor(3*p*u)-3*floor(p*u))*c[15];
 return (acc-sy)*float(v.d);
}
kernel void multiply(device const Block *w [[buffer(0)]],device const float *x [[buffer(1)]],device float *out [[buffer(2)]],constant Args &a [[buffer(3)]],uint group [[threadgroup_position_in_grid]],uint lane [[thread_index_in_threadgroup]]) {
 uint first=group*4,it=lane%8,ix=lane/8;float s0=0,s1=0,s2=0,s3=0;
 for(uint b=ix;b<a.blocks;b+=4) {
  float c[16],sy=0;
  #pragma unroll
  for(uint k=0;k<3;k++) {
   uint g=k<2?2*it+k:16+it;float y[5];
   #pragma unroll
   for(uint j=0;j<5;j++){uint pos=g<16?j*16+g:80+j*8+g-16;y[j]=x[b*128+pos];sy+=y[j];}
   #pragma unroll
   for(uint j=0;j<4;j++)c[k*5+j]=y[j]-3*y[j+1];
   c[k*5+4]=y[4];
  }
  c[15]=x[b*128+120+it];sy+=c[15];
  if(first<a.rows)s0+=dot_reg(w[first*a.blocks+b],c,sy,it);
  if(first+1<a.rows)s1+=dot_reg(w[(first+1)*a.blocks+b],c,sy,it);
  if(first+2<a.rows)s2+=dot_reg(w[(first+2)*a.blocks+b],c,sy,it);
  if(first+3<a.rows)s3+=dot_reg(w[(first+3)*a.blocks+b],c,sy,it);
 }
 float v0=simd_sum(s0),v1=simd_sum(s1),v2=simd_sum(s2),v3=simd_sum(s3);
 if(lane==0){if(first<a.rows)out[first]=v0;if(first+1<a.rows)out[first+1]=v1;if(first+2<a.rows)out[first+2]=v2;if(first+3<a.rows)out[first+3]=v3;}
}
