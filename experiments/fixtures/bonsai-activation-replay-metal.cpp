#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-metal.h"
#include "ggml-alloc.h"
#include <cmath>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>

static std::vector<float> run(ggml_backend_t backend, ggml_type type, const std::vector<unsigned char>& weights, const std::vector<float>& input, size_t width) {
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
    if(ggml_backend_graph_compute(backend,graph)!=GGML_STATUS_SUCCESS)throw std::runtime_error("graph failed");
    std::vector<float> result(rows*columns);ggml_backend_tensor_get(y,result.data(),0,result.size()*sizeof(float));
    ggml_backend_buffer_free(buffer);ggml_free(ctx);return result;
}

int main(int argc,char **argv) {
 if(argc!=8)return 2;
 size_t width=std::stoul(argv[5]),rows=std::stoul(argv[6]),columns=std::stoul(argv[7]);
 auto read=[](const char *p,size_t n){std::vector<unsigned char>b(n);std::ifstream f(p,std::ios::binary);f.read((char*)b.data(),n);if((size_t)f.gcount()!=n||f.peek()!=EOF)throw std::runtime_error("fixture size mismatch");return b;};
 auto ptq=read(argv[1],rows*(width/128)*28),pq=read(argv[2],rows*(width/128)*34),input=read(argv[3],width*columns*4);
 std::vector<float>x(width*columns);memcpy(x.data(),input.data(),input.size());
 auto backend=ggml_backend_metal_init();if(!backend)return 3;
 auto a=run(backend,GGML_TYPE_PTQ1_0,ptq,x,width),b=run(backend,GGML_TYPE_PQ2_0,pq,x,width);
 std::ofstream out(argv[4],std::ios::binary);out.write((char*)a.data(),a.size()*4);out.write((char*)b.data(),b.size()*4);if(!out)return 4;
 for(float v:a)if(!std::isfinite(v))return 5;for(float v:b)if(!std::isfinite(v))return 5;
 ggml_backend_free(backend);return 0;
}
