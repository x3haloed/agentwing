#include <metal_stdlib>
using namespace metal;
struct Block { uchar qs[24]; uchar qh[2]; half d; };
struct Args { uint blocks; uint rows; };
kernel void make_lut(device const float *x [[buffer(0)]],device float *lut [[buffer(1)]],constant Args &a [[buffer(2)]],uint id [[thread_position_in_grid]]) {
 uint block=id/6144,group=(id/256)%24,code=id%256;if(block>=a.blocks)return;
 const int p[6]={1,3,9,27,81,243};float sum=0;
 for(uint j=0;j<5;j++) {
  int trit=((int(code)*p[j+1])>>8)-3*((int(code)*p[j])>>8)-1;
  uint pos=group<16?j*16+group:80+j*8+group-16;
  sum+=float(trit)*x[block*128+pos];
 }
 lut[id]=sum;
}
kernel void multiply_lut(device const Block *w [[buffer(0)]],device const float *x [[buffer(1)]],device const float *lut [[buffer(2)]],device float *out [[buffer(3)]],constant Args &a [[buffer(4)]],uint row [[threadgroup_position_in_grid]],uint lane [[thread_index_in_threadgroup]]) {
 if(row>=a.rows)return;float sum=0;const int p[4]={1,3,9,27};
 for(uint b=lane;b<a.blocks;b+=32) {
  device const Block &v=w[row*a.blocks+b];float dot=0;
  for(uint g=0;g<24;g++)dot+=lut[(b*24+g)*256+v.qs[g]];
  for(uint t=0;t<8;t++) {
   int code=v.qh[t&1],power=p[t>>1];
   int trit=((3*power*code)>>8)-3*((power*code)>>8)-1;
   dot+=float(trit)*x[b*128+120+t];
  }
  sum+=dot*float(v.d);
 }
 float total=simd_sum(sum);if(lane==0)out[row]=total;
}
