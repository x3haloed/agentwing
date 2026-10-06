#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-metal.h"
#include "ggml-alloc.h"
#include <cmath>
#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>

static std::vector<float> run(ggml_backend_t backend, ggml_type type, const std::vector<unsigned char>& weights, const std::vector<float>& input, size_t width) {
    auto start=std::chrono::steady_clock::now();
    ggml_init_params params{1024*1024,nullptr,true};
    auto ctx=ggml_init(params); if(!ctx)throw std::runtime_error("context allocation failed");
    const size_t columns=input.size()/width, rows=weights.size()/ggml_row_size(type,width);
    auto a=ggml_new_tensor_2d(ctx,type,width,rows);
    auto x=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,width,columns);
    auto y=ggml_mul_mat(ctx,a,x);
    auto graph=ggml_new_graph_custom(ctx,16,false);ggml_build_forward_expand(graph,y);
    auto buffer=ggml_backend_alloc_ctx_tensors(ctx,backend);if(!buffer)throw std::runtime_error("backend allocation failed");
    if(ggml_nbytes(a)!=weights.size())throw std::runtime_error("weight layout mismatch");
    ggml_backend_tensor_set(a,weights.data(),0,weights.size());
    ggml_backend_tensor_set(x,input.data(),0,input.size()*sizeof(float));
    auto installed=std::chrono::steady_clock::now();
    if(ggml_backend_graph_compute(backend,graph)!=GGML_STATUS_SUCCESS)throw std::runtime_error("graph failed");
    auto computed=std::chrono::steady_clock::now();
    std::vector<float> result(rows*columns);ggml_backend_tensor_get(y,result.data(),0,result.size()*sizeof(float));
    ggml_backend_buffer_free(buffer);ggml_free(ctx);
    auto end=std::chrono::steady_clock::now();
    auto ms=[](auto a,auto b){return std::chrono::duration<double,std::milli>(b-a).count();};
    std::cout<<type<<"\t"<<columns<<"\t"<<ms(start,installed)<<"\t"<<ms(installed,computed)<<"\t"<<ms(computed,end)<<"\t"<<ms(start,end)<<"\n";
    return result;
}

int main(int argc,char **argv) {
 if(argc!=7)return 2;
 size_t width=std::stoul(argv[4]),rows=std::stoul(argv[5]),columns=std::stoul(argv[6]);
 auto read=[](const char *p,size_t n){std::vector<unsigned char>b(n);std::ifstream f(p,std::ios::binary);f.read((char*)b.data(),n);if((size_t)f.gcount()!=n)throw std::runtime_error("short fixture");return b;};
 auto ptq=read(argv[1],rows*(width/128)*28),pq=read(argv[2],rows*(width/128)*34),input=read(argv[3],width*columns*4);
 std::vector<float>x(width*columns);memcpy(x.data(),input.data(),input.size());
 auto backend=ggml_backend_metal_init();if(!backend)return 3;
 for(int rep=0;rep<3;rep++)for(int arm:{0,1,1,0}) {
  auto out=run(backend,arm?GGML_TYPE_PQ2_0:GGML_TYPE_PTQ1_0,arm?pq:ptq,x,width);
  for(float v:out)if(!std::isfinite(v))return 5;
 }
 ggml_backend_free(backend);return 0;
}
