#include <metal_stdlib>
using namespace metal;
struct Block { uchar qs[24]; uchar qh[2]; half d; };
struct Args { uint blocks; uint rows; };
kernel void make_lut(device const float *x [[buffer(0)]],device float *lut [[buffer(1)]],constant Args &a [[buffer(2)]],uint id [[thread_position_in_grid]]) {
 uint block=id/864,group=(id/36)%24,slot=id%36;if(block>=a.blocks)return;
 bool left=slot<27;uint code=left?slot:slot-27,count=left?3:2;
 const uint powers[3]={1,3,9};float sum=0;
 for(uint j=0;j<count;j++) {
  int trit=int((code/powers[count-1-j])%3)-1;uint digit=left?j:j+3;
  uint pos=group<16?digit*16+group:80+digit*8+group-16;
  sum+=float(trit)*x[block*128+pos];
 }
 lut[id]=sum;
}
inline float lookup(device const float *lut,uint b,uint g,uint code) {
 uint left=(27*code)>>8,right=((243*code)>>8)-9*left,base=(b*24+g)*36;
 return lut[base+left]+lut[base+27+right];
}
inline float dot_lane(device const Block &v,device const float *x,device const float *lut,uint b,uint it) {
 float dot=lookup(lut,b,2*it,v.qs[2*it]);
 dot+=lookup(lut,b,2*it+1,v.qs[2*it+1]);
 dot+=lookup(lut,b,16+it,v.qs[16+it]);
 int power=it<2?1:it<4?3:it<6?9:27,code=v.qh[it&1];
 int trit=((3*power*code)>>8)-3*((power*code)>>8)-1;
 return (dot+float(trit)*x[b*128+120+it])*float(v.d);
}
kernel void multiply_lut(device const Block *w [[buffer(0)]],device const float *x [[buffer(1)]],device const float *lut [[buffer(2)]],device float *out [[buffer(3)]],constant Args &a [[buffer(4)]],uint group [[threadgroup_position_in_grid]],uint lane [[thread_index_in_threadgroup]]) {
 uint first=group*4,it=lane%8,ix=lane/8;float s0=0,s1=0,s2=0,s3=0;
 for(uint b=ix;b<a.blocks;b+=4) {
  if(first<a.rows)s0+=dot_lane(w[first*a.blocks+b],x,lut,b,it);
  if(first+1<a.rows)s1+=dot_lane(w[(first+1)*a.blocks+b],x,lut,b,it);
  if(first+2<a.rows)s2+=dot_lane(w[(first+2)*a.blocks+b],x,lut,b,it);
  if(first+3<a.rows)s3+=dot_lane(w[(first+3)*a.blocks+b],x,lut,b,it);
 }
 float v0=simd_sum(s0),v1=simd_sum(s1),v2=simd_sum(s2),v3=simd_sum(s3);
 if(lane==0) {
  if(first<a.rows)out[first]=v0;if(first+1<a.rows)out[first+1]=v1;
  if(first+2<a.rows)out[first+2]=v2;if(first+3<a.rows)out[first+3]=v3;
 }
}
