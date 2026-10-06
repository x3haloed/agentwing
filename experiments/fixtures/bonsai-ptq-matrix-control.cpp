#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-metal.h"
#include <chrono>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <vector>
int main(int argc,char **argv) {
 if(argc!=6)return 2;
 const int width=std::stoi(argv[4]),rows=std::stoi(argv[5]);if(width%128||width<=0||rows<=0)return 3;
 std::vector<unsigned char>w(size_t(rows)*width/128*28);std::vector<float>x(width),out(rows);
 std::ifstream wf(argv[1],std::ios::binary),xf(argv[2],std::ios::binary);
 if(!wf.read((char*)w.data(),w.size())||!xf.read((char*)x.data(),x.size()*4))return 4;
 auto backend=ggml_backend_metal_init();if(!backend)return 5;
 auto ctx=ggml_init({1024*1024,nullptr,true});if(!ctx)return 6;
 auto weights=ggml_new_tensor_2d(ctx,GGML_TYPE_PTQ1_0,width,rows);
 auto input=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,width,1);auto output=ggml_mul_mat(ctx,weights,input);
 auto graph=ggml_new_graph_custom(ctx,16,false);ggml_build_forward_expand(graph,output);
 auto buffer=ggml_backend_alloc_ctx_tensors(ctx,backend);if(!buffer)return 7;
 ggml_backend_tensor_set(weights,w.data(),0,w.size());ggml_backend_tensor_set(input,x.data(),0,x.size()*4);
 for(int i=0;i<5;i++) {
  auto start=std::chrono::steady_clock::now();
  if(ggml_backend_graph_compute(backend,graph)!=GGML_STATUS_SUCCESS)return 8;
  ggml_backend_tensor_get(output,out.data(),0,out.size()*4);
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  printf("iteration=%d compute_and_readback_seconds=%.9f\n",i,seconds);fflush(stdout);
 }
 for(float v:out)if(!std::isfinite(v))return 9;
 FILE *f=fopen(argv[3],"wb");if(!f||fwrite(out.data(),4,out.size(),f)!=out.size())return 10;fclose(f);
 ggml_backend_buffer_free(buffer);ggml_free(ctx);ggml_backend_free(backend);return 0;
}
