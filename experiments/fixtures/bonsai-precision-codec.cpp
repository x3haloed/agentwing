#include "ggml.h"
#include <cmath>
#include <cstring>
#include <cstdint>
static const float turbo_cpu_s1[128] = {
    -1,1,1,-1,-1,1,-1,1,-1,-1,1,1,1,1,1,1,1,-1,1,-1,1,-1,-1,1,1,1,-1,1,1,-1,-1,-1,
    -1,1,1,-1,1,1,-1,1,-1,1,1,-1,-1,1,-1,1,1,1,1,-1,-1,-1,-1,-1,1,-1,1,1,1,1,-1,1,
    -1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,1,-1,-1,1,1,1,-1,-1,1,1,-1,1,1,-1,1,-1,
    -1,1,1,-1,1,-1,1,-1,1,1,1,1,-1,1,-1,1,1,-1,1,1,-1,-1,-1,-1,-1,1,1,-1,1,1,-1,1
};

static const float turbo_cpu_s2[128] = {
    1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,-1,-1,1,-1,1,-1,1,-1,-1,1,-1,1,1,1,
    1,1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,1,1,1,-1,1,-1,1,1,1,-1,-1,1,-1,-1,-1,-1,-1,-1,1,1,
    1,-1,1,-1,-1,-1,-1,1,-1,1,-1,1,-1,-1,1,1,-1,1,-1,1,1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,
    1,-1,1,1,1,-1,-1,1,-1,1,-1,1,1,-1,-1,1,-1,1,-1,1,1,-1,1,-1,1,-1,-1,-1,-1,-1,1,-1
};

/* ---------- CPU forward WHT (in-place, group_size elements) ---------- */

static void turbo_cpu_fwht(float * x, int group_size) {
    const float * s1 = turbo_cpu_s1;
    const float * s2 = turbo_cpu_s2;
    const float inv_sqrt = (group_size == 128) ? 0.08838834764831845f : 0.125f;

    // signs1
    for (int i = 0; i < group_size; i++) x[i] *= s1[i];

    // butterfly stages
    for (int h = 1; h < group_size; h *= 2) {
        for (int i = 0; i < group_size; i += h * 2) {
            for (int j = i; j < i + h; j++) {
                float a = x[j], b = x[j + h];
                x[j]     = a + b;
                x[j + h] = a - b;
            }
        }
    }

    // normalize + signs2
    for (int i = 0; i < group_size; i++) x[i] *= inv_sqrt * s2[i];
}


extern "C" void turbo_cpu_fwht_inverse(float *,int);
extern "C" void encode_precision_book(const float *x,int count,int bits,const float *c,const float *cuts,unsigned char *packed,float *out) {
 for(int b=0;b<count/128;b++) {
  float norm2=0;for(int i=0;i<128;i++)norm2+=x[b*128+i]*x[b*128+i];float norm=sqrtf(norm2),inv=norm>1e-10f?1.0f/norm:0;float z[128];for(int i=0;i<128;i++)z[i]=x[b*128+i]*inv;turbo_cpu_fwht(z,128);
  int bytes=4+128*bits/8;unsigned char *p=packed+b*bytes;memset(p,0,bytes);float recon2=0;int ids[128];
  for(int i=0;i<128;i++){int j=0;while(j<(1<<bits)-1 && z[i]>=cuts[j])j++;ids[i]=j;int bit=i*bits;for(int k=0;k<bits;k++)p[4+(bit+k)/8]|=((j>>k)&1)<<((bit+k)%8);recon2+=c[j]*c[j];}
  float recon=sqrtf(recon2);ggml_fp16_t scale=ggml_fp32_to_fp16(recon>1e-10f?norm/recon:norm);memcpy(p,&scale,2);float d=ggml_fp16_to_fp32(scale);
  for(int i=0;i<128;i++)out[b*128+i]=c[ids[i]]*d;turbo_cpu_fwht_inverse(out+b*128,128);
 }
}
