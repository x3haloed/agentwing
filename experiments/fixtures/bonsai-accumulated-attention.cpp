#include "llama.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <stdexcept>
struct Capture { std::string dir; size_t bytes=0; int count=0; bool failed=false; bool enabled=false; };
static int layer(ggml_tensor *t) {
 if(t->op!=GGML_OP_FLASH_ATTN_EXT)return -1;
 auto *v=t->src[1];
 for(int depth=0;v && depth<12;depth++,v=v->src[0]) {
  int il=-1;if(sscanf(v->name,"cache_k_l%d",&il)==1)return il;
 }
 return -1;
}
static bool callback(ggml_tensor *t,bool ask,void *userdata) {
 auto &c=*static_cast<Capture*>(userdata);int il=layer(t);bool wanted=c.enabled&&(il==3||il==31||il==63);
 if(ask)return wanted;if(!wanted){c.failed=true;return false;}
 float scale;memcpy(&scale,t->op_params,4);
 for(int role=0;role<5;role++) {
  ggml_tensor *v=role==4?t:t->src[role];if(!v){c.failed=true;return false;}
  size_t n=ggml_nbytes(v);if((v->type!=GGML_TYPE_F32&&v->type!=GGML_TYPE_F16)||n>32*1024*1024||c.bytes+n>128*1024*1024){c.failed=true;return false;}
  std::vector<unsigned char>b(n);ggml_backend_tensor_get(v,b.data(),0,n);
  std::string path=c.dir+"/"+std::to_string(il)+"-"+std::to_string(role)+".bin";FILE*f=fopen(path.c_str(),"wb");if(!f){c.failed=true;return false;}bool ok=fwrite(b.data(),1,n,f)==n;fclose(f);if(!ok){c.failed=true;return false;}
  printf("%d\t%d\t%d\t%zu",il,role,(int)v->type,n);
  for(int j=0;j<4;j++)printf("\t%lld",(long long)v->ne[j]);
  for(int j=0;j<4;j++)printf("\t%zu",v->nb[j]);
  printf("\t%.9g\t%s\n",scale,v->name);fflush(stdout);c.bytes+=n;
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
 auto *sampler=llama_sampler_chain_init(llama_sampler_chain_default_params());
 llama_sampler_chain_add(sampler,llama_sampler_init_penalties(llama_vocab_n_tokens(vocab),64,1.0f,0.0f,0.0f));
 llama_sampler_chain_add(sampler,llama_sampler_init_top_k(20));
 llama_sampler_chain_add(sampler,llama_sampler_init_top_p(0.95f,1));
 llama_sampler_chain_add(sampler,llama_sampler_init_min_p(0.05f,1));
 llama_sampler_chain_add(sampler,llama_sampler_init_temp(1.0f));
 llama_sampler_chain_add(sampler,llama_sampler_init_dist(42));
 int generated=0;
 while(status==0 && generated<32) {
  llama_token next=llama_sampler_sample(sampler,ctx,-1);
  fprintf(stderr,"TOKEN\t%d\t%d\n",generated,next);
  if(llama_vocab_is_eog(vocab,next))break;
  cap.enabled=generated==31;
  status=llama_decode(ctx,llama_batch_get_one(&next,1));generated++;
 }
 fprintf(stderr,"STATE\t%d\t%d\n",n,generated);
 llama_sampler_free(sampler);llama_free(ctx);llama_model_free(model);llama_backend_free();
 return status==0&&!cap.failed&&generated==32&&cap.count==3?0:5;
}
