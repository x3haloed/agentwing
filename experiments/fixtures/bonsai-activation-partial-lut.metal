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
kernel void multiply_lut(device const Block *w [[buffer(0)]],device const float *x [[buffer(1)]],device const float *lut [[buffer(2)]],device float *out [[buffer(3)]],constant Args &a [[buffer(4)]],uint group [[threadgroup_position_in_grid]],uint lane [[thread_index_in_threadgroup]]) {
 uint first=group*4,it=lane%8,ix=lane/8;
 float sums[4]={0,0,0,0};const int p[4]={1,3,9,27};
 for(uint b=ix;b<a.blocks;b+=4) {
  for(uint row=0;row<4;row++) {
   if(first+row>=a.rows)continue;
   device const Block &v=w[(first+row)*a.blocks+b];
   float dot=lookup(lut,b,2*it,v.qs[2*it]);
   dot+=lookup(lut,b,2*it+1,v.qs[2*it+1]);
   dot+=lookup(lut,b,16+it,v.qs[16+it]);
   int code=v.qh[it&1],power=p[it>>1];
   int trit=((3*power*code)>>8)-3*((power*code)>>8)-1;
   dot+=float(trit)*x[b*128+120+it];
   sums[row]+=dot*float(v.d);
  }
 }
 for(uint row=0;row<4;row++) {
  float total=simd_sum(sums[row]);if(lane==0&&first+row<a.rows)out[first+row]=total;
 }
}
