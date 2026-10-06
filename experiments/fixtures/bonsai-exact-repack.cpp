#include <cstdint>
#include <cstddef>
#include <cstring>
#include <limits>
extern "C" int repack_ptq_blocks(const uint8_t *src, size_t size, uint8_t *dst, size_t capacity) {
    if(size%28 || size/28>std::numeric_limits<size_t>::max()/34 || capacity!=(size/28)*34)return 0;
    static const int powers[5]={1,3,9,27,81};
    for(size_t block=0;block<size/28;block++) {
        const auto in=src+block*28;auto out=dst+block*34;
        std::memset(out,0,34);std::memcpy(out,in+26,2);
        for(int e=0;e<128;e++) {
            int b,n;
            if(e<80){b=in[e&15];n=e>>4;}
            else if(e<120){int t=e-80;b=in[16+(t&7)];n=t>>3;}
            else{int t=e-120;b=in[24+(t&1)];n=t>>1;}
            int q=(((b*powers[n])&255)*3)>>8;
            out[2+e/4]|=q<<(2*(e%4));
        }
    }
    return 1;
}
