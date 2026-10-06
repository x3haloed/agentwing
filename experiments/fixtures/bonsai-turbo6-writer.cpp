#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-metal.h"
#include <fstream>
#include <vector>
#include <stdexcept>
#include <cstdio>
#include <chrono>
int main(int argc,char **argv) {
 if(argc!=5)return 2;
 int bits=atoi(argv[1]);ggml_type type=bits==6?GGML_TYPE_TURBO6_0:GGML_TYPE_TURBO4_0;
 auto backend=ggml_backend_metal_init();if(!backend)return 3;
 auto ctx=ggml_init({1024*1024,nullptr,true});
 auto dst=ggml_new_tensor_2d(ctx,type,256,192);auto src=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,256,192);auto idx=ggml_new_tensor_1d(ctx,GGML_TYPE_I64,192);
 auto op=ggml_set_rows(ctx,dst,src,idx);if(!ggml_backend_supports_op(backend,op))return 4;
 auto graph=ggml_new_graph_custom(ctx,16,false);ggml_build_forward_expand(graph,op);
 auto buffer=ggml_backend_alloc_ctx_tensors(ctx,backend);if(!buffer)return 5;
 std::vector<float>input(256*192);std::ifstream f(argv[2],std::ios::binary);f.read((char*)input.data(),input.size()*4);if(f.gcount()!=input.size()*4)return 6;
 std::vector<int64_t>indices(192);for(int i=0;i<192;i++)indices[i]=191-i;
 ggml_backend_tensor_set(src,input.data(),0,input.size()*4);ggml_backend_tensor_set(idx,indices.data(),0,indices.size()*8);
 std::vector<unsigned char>output(ggml_nbytes(op));
 for(int iteration=0;iteration<5;iteration++) {
  auto start=std::chrono::steady_clock::now();
  for(int repeat=0;repeat<64;repeat++) {
  if(ggml_backend_graph_compute(backend,graph)!=GGML_STATUS_SUCCESS)return 7;
  ggml_backend_tensor_get(op,output.data(),0,output.size());
  }
  printf("iteration=%d compute_readback_seconds=%.9f\n",iteration,std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());fflush(stdout);
 }
std::ofstream out(argv[3],std::ios::binary);out.write((char*)output.data(),output.size());out.close();
 printf("supported=1 bytes=%zu marker=%s\n",output.size(),argv[4]);
 ggml_backend_buffer_free(buffer);ggml_free(ctx);ggml_backend_free(backend);return 0;
}
