#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-metal.h"
#include "ggml-cpu.h"
#include <fstream>
#include <vector>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <chrono>
static void load(ggml_tensor*t,const std::string&p) {
 std::vector<unsigned char>b(ggml_nbytes(t));std::ifstream f(p,std::ios::binary);f.read((char*)b.data(),b.size());if((size_t)f.gcount()!=b.size())throw std::runtime_error("short input");ggml_backend_tensor_set(t,b.data(),0,b.size());
}
int main(int argc,char**argv) {
 if(argc!=5)return 2;bool turbo=true;bool q8=!strcmp(argv[1],"turbo");int nq=atoi(argv[4]);if((strcmp(argv[1],"f16-turbo")&&!q8)||(nq!=1&&nq!=128))return 2;auto backend=ggml_backend_metal_init();if(!backend)return 3;
 auto ctx=ggml_init({1024*1024,nullptr,true});auto q=ggml_new_tensor_4d(ctx,GGML_TYPE_F32,256,nq,24,1);auto k=ggml_new_tensor_4d(ctx,q8?GGML_TYPE_Q8_0:GGML_TYPE_F16,256,64,4,1);auto v=ggml_new_tensor_4d(ctx,turbo?GGML_TYPE_TURBO4_0:GGML_TYPE_F16,256,64,4,1);auto mask=ggml_new_tensor_2d(ctx,GGML_TYPE_F16,64,((nq+31)/32)*32);
 auto attention=ggml_flash_attn_ext(ctx,q,k,v,mask,.0625f,0,0);auto y=turbo?ggml_turbo_inverse(ctx,attention):attention;if(!ggml_backend_supports_op(backend,attention)||!ggml_backend_supports_op(backend,y))return 4;auto cpu=ggml_backend_cpu_init();if(turbo&&ggml_backend_supports_op(cpu,y))return 8;ggml_backend_free(cpu);
 auto graph=ggml_new_graph_custom(ctx,16,false);ggml_build_forward_expand(graph,y);auto buffer=ggml_backend_alloc_ctx_tensors(ctx,backend);if(!buffer)return 5;
 std::string d=argv[2];load(q,d+"/q.bin");load(k,d+"/k.bin");load(v,d+"/v.bin");std::vector<unsigned char>m(64*((nq+31)/32)*32*2);std::ifstream f(d+"/mask.bin",std::ios::binary);f.read((char*)m.data(),128);if(f.gcount()!=128)return 6;for(int i=1;i<((nq+31)/32)*32;i++)memcpy(m.data()+i*128,m.data(),128);ggml_backend_tensor_set(mask,m.data(),0,m.size());
 std::vector<unsigned char>output(ggml_nbytes(y));
 for(int iteration=0;iteration<5;iteration++) {auto start=std::chrono::steady_clock::now();
  for(int repeat=0;repeat<16;repeat++) {
   if(ggml_backend_graph_compute(backend,graph)!=GGML_STATUS_SUCCESS)return 7;
   ggml_backend_tensor_get(y,output.data(),0,output.size());
  }
  printf("iteration=%d compute_readback_seconds=%.9f\n",iteration,std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());fflush(stdout);
 }
std::ofstream out(argv[3],std::ios::binary);out.write((char*)output.data(),output.size());out.close();printf("supported=1 bytes=%zu\n",output.size());ggml_backend_buffer_free(buffer);ggml_free(ctx);ggml_backend_free(backend);return 0;
}
