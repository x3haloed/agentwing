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

static std::vector<float> run(ggml_backend_t backend, ggml_type type, const std::vector<unsigned char>& weights, const std::vector<float>& input) {
    ggml_init_params params{1024*1024,nullptr,true};
    auto ctx=ggml_init(params); if(!ctx)throw std::runtime_error("context allocation failed");
    auto a=ggml_new_tensor_2d(ctx,type,128,64);
    auto x=ggml_new_tensor_2d(ctx,GGML_TYPE_F32,128,1);
    auto y=ggml_mul_mat(ctx,a,x);
    auto graph=ggml_new_graph_custom(ctx,16,false);ggml_build_forward_expand(graph,y);
    auto buffer=ggml_backend_alloc_ctx_tensors(ctx,backend);if(!buffer)throw std::runtime_error("backend allocation failed");
    if(ggml_nbytes(a)!=weights.size())throw std::runtime_error("weight layout mismatch");
    ggml_backend_tensor_set(a,weights.data(),0,weights.size());
    ggml_backend_tensor_set(x,input.data(),0,input.size()*sizeof(float));
    if(ggml_backend_graph_compute(backend,graph)!=GGML_STATUS_SUCCESS)throw std::runtime_error("graph failed");
    std::vector<float> result(64);ggml_backend_tensor_get(y,result.data(),0,result.size()*sizeof(float));
    ggml_backend_buffer_free(buffer);ggml_free(ctx);return result;
}

int main(int argc,char**argv) {
    if(argc!=4)return 2;
    std::ofstream raw(argv[3],std::ios::binary);if(!raw)throw std::runtime_error("raw output open failed");
    auto read=[](const char* path,size_t count){std::vector<unsigned char>b(count);std::ifstream f(path,std::ios::binary);f.read((char*)b.data(),count);if((size_t)f.gcount()!=count)throw std::runtime_error("short fixture");return b;};
    auto ptq=read(argv[1],64*28),pq=read(argv[2],64*34);
    auto backend=ggml_backend_metal_init();if(!backend)throw std::runtime_error("Metal backend unavailable");
    double diff2=0,norm2=0,maxabs=0;
    for(int pattern=0;pattern<4;pattern++) {
        std::vector<float>x(128);for(int i=0;i<128;i++)x[i]=(pattern==0)?1.0f:(pattern==1)?((i%2)?-1.0f:1.0f):(pattern==2)?std::sin(i*0.17f):((i==17)?1.0f:0.0f);
        auto a=run(backend,GGML_TYPE_PTQ1_0,ptq,x);auto b=run(backend,GGML_TYPE_PQ2_0,pq,x);
        raw.write((const char*)x.data(),128*sizeof(float));raw.write((const char*)a.data(),64*sizeof(float));raw.write((const char*)b.data(),64*sizeof(float));if(!raw)throw std::runtime_error("raw output write failed");
        for(int i=0;i<64;i++){if(!std::isfinite(a[i])||!std::isfinite(b[i]))throw std::runtime_error("nonfinite output");double d=a[i]-b[i];diff2+=d*d;norm2+=(double)a[i]*a[i];maxabs=std::max(maxabs,std::abs(d));}
    }
    ggml_backend_free(backend);
    double relative=std::sqrt(diff2/std::max(norm2,1e-30));
    std::cout<<"{\"relative_l2\":"<<relative<<",\"maximum_absolute_difference\":"<<maxabs<<",\"output_values\":256,\"scope\":\"Tiny native Metal codec compatibility only; rearranged sampled real blocks with synthetic inputs, no performance or activation claim\"}\n";
    return relative<=1e-4?0:1;
}
