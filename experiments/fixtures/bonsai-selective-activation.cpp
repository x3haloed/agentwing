#include "llama.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <stdexcept>
struct Capture { std::string dir; size_t bytes=0; int count=0; bool failed=false; };
static bool selected(ggml_tensor *t) {
 if(t->op!=GGML_OP_MUL_MAT || !t->src[0]) return false;
 const char *n=t->src[0]->name;
 return !strcmp(n,"blk.0.ffn_up.weight") || !strcmp(n,"blk.31.ffn_up.weight") || !strcmp(n,"blk.63.ffn_up.weight");
}
static bool callback(ggml_tensor *t,bool ask,void *userdata) {
 auto &c=*static_cast<Capture*>(userdata);
 if(ask) return selected(t);
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
 if(argc!=4)return 2;
 ggml_backend_load_all();llama_backend_init();
 auto mp=llama_model_default_params();mp.n_gpu_layers=999;
 auto *model=llama_model_load_from_file(argv[1],mp);if(!model)return 3;
 Capture cap;cap.dir=argv[2];auto cp=llama_context_default_params();
 cp.n_ctx=2048;cp.n_batch=128;cp.n_ubatch=128;cp.n_seq_max=1;cp.n_rs_seq=0;
 cp.type_k=GGML_TYPE_F16;cp.type_v=GGML_TYPE_F16;cp.cb_eval=callback;cp.cb_eval_user_data=&cap;
 auto *ctx=llama_init_from_model(model,cp);if(!ctx){llama_model_free(model);return 4;}
 auto *vocab=llama_model_get_vocab(model);std::vector<llama_token> tokens(128);
 int n=llama_tokenize(vocab,argv[3],strlen(argv[3]),tokens.data(),tokens.size(),true,true);
 int status=n>0&&n<=128?llama_decode(ctx,llama_batch_get_one(tokens.data(),n)):1;
 llama_free(ctx);llama_model_free(model);llama_backend_free();
 return status==0&&!cap.failed&&cap.count==3?0:5;
}
