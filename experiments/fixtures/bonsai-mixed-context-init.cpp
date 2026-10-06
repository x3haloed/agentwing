#include "llama.h"
#include <cstdio>
#include <cmath>
#include <cstring>
#include <string>
#include <vector>
#include <stdexcept>
#include <fstream>
#include <sstream>
struct Capture { std::string dir; size_t bytes=0; int count=0; bool failed=false; bool enabled=false; };
static bool selected(ggml_tensor *t) {
 if(t->op!=GGML_OP_MUL_MAT || !t->src[0]) return false;
 const char *n=t->src[0]->name;
 return !strcmp(n,"blk.0.ssm_out.weight") || !strcmp(n,"blk.0.ffn_down.weight") || !strcmp(n,"blk.31.attn_output.weight") || !strcmp(n,"blk.31.ffn_down.weight") || !strcmp(n,"blk.63.attn_output.weight") || !strcmp(n,"blk.63.ffn_down.weight");
}
static bool callback(ggml_tensor *t,bool ask,void *userdata) {
 auto &c=*static_cast<Capture*>(userdata);
 if(ask) return c.enabled && selected(t);
 if(!selected(t)) {c.failed=true;return false;}
 for(int k=0;k<2;k++) {
  ggml_tensor *v=k==0?t->src[1]:t;
  size_t n=ggml_nbytes(v);
  if(v->type!=GGML_TYPE_F32 || !ggml_is_contiguous(v) || n>8*1024*1024 || c.bytes+n>64*1024*1024) {c.failed=true;return false;}
  std::vector<unsigned char> b(n);ggml_backend_tensor_get(v,b.data(),0,n);
  std::string path=c.dir+"/"+std::to_string(c.count)+"-"+std::to_string(k)+".bin";
  FILE *f=fopen(path.c_str(),"wb");if(!f){c.failed=true;return false;}
  bool ok=fwrite(b.data(),1,n,f)==n;fclose(f);if(!ok){c.failed=true;return false;}
  printf("%d\t%d\t%s\t%s\t%lld\t%lld\t%zu\n",c.count,k,t->src[0]->name,v->name,(long long)v->ne[0],(long long)v->ne[1],n);fflush(stdout);c.bytes+=n;
 }
 c.count++;return true;
}
int main(int argc,char **argv) {
 if(argc!=5)return 2;
 std::ifstream input(argv[3]);std::ostringstream buffer;buffer<<input.rdbuf();std::string prompt=buffer.str();if(!input || prompt.empty())return 9;
 bool q8=!strcmp(argv[4],"turbo") || !strcmp(argv[4],"q8-f16"); bool tv=!strcmp(argv[4],"turbo") || !strcmp(argv[4],"f16-turbo");if(strcmp(argv[4],"turbo") && strcmp(argv[4],"f16") && strcmp(argv[4],"q8-f16") && strcmp(argv[4],"f16-turbo"))return 10;
 ggml_backend_load_all_from_path("/Users/chad/Models/agentwing/runtime-builds/prism-turbo-mixed-graph/bin");llama_backend_init();
 auto mp=llama_model_default_params();mp.n_gpu_layers=999;
 auto *model=llama_model_load_from_file(argv[1],mp);if(!model)return 3;
 Capture cap;cap.dir=argv[2];auto cp=llama_context_default_params();
 cp.n_ctx=16384;cp.n_batch=128;cp.n_ubatch=128;cp.n_seq_max=1;cp.n_rs_seq=0;
 cp.type_k=q8?GGML_TYPE_Q8_0:GGML_TYPE_F16;cp.type_v=tv?GGML_TYPE_TURBO4_0:GGML_TYPE_F16;cp.flash_attn_type=LLAMA_FLASH_ATTN_TYPE_ENABLED;cp.cb_eval=callback;cp.cb_eval_user_data=&cap;
 auto *ctx=llama_init_from_model(model,cp);if(!ctx){llama_model_free(model);return 4;}
 printf("CONTEXT_INIT_OK\n");llama_free(ctx);llama_model_free(model);llama_backend_free();return 0;
}
