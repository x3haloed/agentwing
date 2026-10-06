#include <metal_stdlib>
using namespace metal;
constant float s1[128]={
    -1,1,1,-1,-1,1,-1,1,-1,-1,1,1,1,1,1,1,1,-1,1,-1,1,-1,-1,1,1,1,-1,1,1,-1,-1,-1,
    -1,1,1,-1,1,1,-1,1,-1,1,1,-1,-1,1,-1,1,1,1,1,-1,-1,-1,-1,-1,1,-1,1,1,1,1,-1,1,
    -1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,1,-1,-1,1,1,1,-1,-1,1,1,-1,1,1,-1,1,-1,
    -1,1,1,-1,1,-1,1,-1,1,1,1,1,-1,1,-1,1,1,-1,1,1,-1,-1,-1,-1,-1,1,1,-1,1,1,-1,1
};
constant float s2[128]={
    1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,-1,-1,1,-1,1,-1,1,-1,-1,1,-1,1,1,1,
    1,1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,1,1,1,-1,1,-1,1,1,1,-1,-1,1,-1,-1,-1,-1,-1,-1,1,1,
    1,-1,1,-1,-1,-1,-1,1,-1,1,-1,1,-1,-1,1,1,-1,1,-1,1,1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,
    1,-1,1,1,1,-1,-1,1,-1,1,-1,1,1,-1,-1,1,-1,1,-1,1,1,-1,1,-1,1,-1,-1,-1,-1,-1,1,-1
};
void wht(thread float *x){for(int h=1;h<128;h*=2)for(int i=0;i<128;i+=2*h)for(int j=i;j<i+h;j++){float a=x[j],b=x[j+h];x[j]=a+b;x[j+h]=a-b;}for(int j=0;j<128;j++)x[j]*=0.08838834764831845f;}
kernel void encode_values(device const float *src [[buffer(0)]],device const float *book [[buffer(1)]],device uchar *dst [[buffer(2)]],constant uint &bits [[buffer(3)]],device float *trace [[buffer(4)]],uint b [[thread_position_in_grid]]){
 uint levels=1u<<bits,size=4+16*bits;device uchar *p=dst+b*size;float x[128],n=0;
 for(uint j=0;j<128;j++)n+=src[b*128+j]*src[b*128+j];n=sqrt(n);float inv=n>1e-10f?1.f/n:0;
 for(uint j=0;j<128;j++)x[j]=src[b*128+j]*inv*s1[j];wht(x);for(uint j=0;j<128;j++)x[j]*=s2[j];for(uint j=0;j<128;j++)trace[b*128+j]=x[j];
 uint ids[128];float rn=0;for(uint j=0;j<128;j++){uint lo=0,hi=levels-1;while(lo<hi){uint m=(lo+hi)/2;if(x[j]>=book[levels+m])lo=m+1;else hi=m;}ids[j]=lo;rn+=book[lo]*book[lo];}
 rn=sqrt(rn);half scale=half(rn>1e-10f?n/rn:n);*((device half*)p)=scale;p[2]=0;p[3]=0;
 if(bits==4){for(uint j=0;j<64;j++)p[4+j]=uchar(ids[2*j]|(ids[2*j+1]<<4));}
 else{for(uint j=0;j<32;j++){uint v=ids[4*j]|(ids[4*j+1]<<6)|(ids[4*j+2]<<12)|(ids[4*j+3]<<18);p[4+3*j]=uchar(v);p[5+3*j]=uchar(v>>8);p[6+3*j]=uchar(v>>16);}}
}
kernel void decode_values(device const uchar *src [[buffer(0)]],device const float *book [[buffer(1)]],device float *dst [[buffer(2)]],constant uint &bits [[buffer(3)]],uint b [[thread_position_in_grid]]){
 uint size=4+16*bits;device const uchar *p=src+b*size;float scale=float(*((device const half*)p));float x[128];
 for(uint j=0;j<128;j++){uint bit=j*bits,byte=bit/8,shift=bit%8;uint v=p[4+byte];if(shift+bits>8)v|=uint(p[5+byte])<<8;uint id=(v>>shift)&((1u<<bits)-1);x[j]=book[id]*scale*s2[j];}wht(x);for(uint j=0;j<128;j++)dst[b*128+j]=x[j]*s1[j];
}
