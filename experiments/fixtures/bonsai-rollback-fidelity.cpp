#include "llama.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>
static std::vector<llama_token> load(const char *p) {
 std::ifstream f(p,std::ios::binary);std::vector<llama_token> v;llama_token t;
 while(f.read((char*)&t,4))v.push_back(t);return v;
}
int main(int argc,char **argv) {
 if(argc!=5)return 2;
 llama_backend_init();auto mp=llama_model_default_params();mp.n_gpu_layers=999;
 auto *model=llama_model_load_from_file(argv[1],mp);if(!model)return 3;
 auto prefix=load(argv[2]),ids=load(argv[3]);if(prefix.empty()||ids.size()<4)return 4;
 const int nv=llama_vocab_n_tokens(llama_model_get_vocab(model));
 for(int accepted=0;accepted<3;accepted++)for(int arm=0;arm<2;arm++) {
  auto cp=llama_context_default_params();cp.n_ctx=16384;cp.n_batch=128;cp.n_ubatch=128;cp.n_seq_max=1;cp.n_rs_seq=3;
  cp.type_k=GGML_TYPE_Q8_0;cp.type_v=GGML_TYPE_TURBO4_0;cp.flash_attn_type=LLAMA_FLASH_ATTN_TYPE_ENABLED;
  auto *ctx=llama_init_from_model(model,cp);if(!ctx)return 5;
  for(size_t j=0;j<prefix.size();j+=128)if(llama_decode(ctx,llama_batch_get_one(prefix.data()+j,std::min(size_t(128),prefix.size()-j))))return 6;
  if(arm==0) {
   for(int j=0;j<=accepted+1;j++)if(llama_decode(ctx,llama_batch_get_one(ids.data()+j,1)))return 7;
  } else {
   std::vector<llama_token> draft(ids.begin(),ids.begin()+4);
   for(int j=accepted+1;j<4;j++)draft[j]=(draft[j]+1001)%nv;
   if(llama_decode(ctx,llama_batch_get_one(draft.data(),4)))return 8;
   if(!llama_memory_seq_rm(llama_get_memory(ctx),0,prefix.size()+accepted+1,-1))return 9;
   if(llama_decode(ctx,llama_batch_get_one(ids.data()+accepted+1,1)))return 10;
  }
  std::string path=std::string(argv[4])+"/"+std::to_string(accepted)+"-"+(arm?"rollback":"control")+".bin";
  FILE *f=fopen(path.c_str(),"wb");if(!f)return 11;
  auto *logits=llama_get_logits_ith(ctx,-1);if(!logits||fwrite(logits,4,nv,f)!=(size_t)nv)return 12;fclose(f);
  printf("accepted=%d arm=%d rollback=%d vocab=%d\n",accepted,arm,3-accepted,nv);fflush(stdout);llama_free(ctx);
 }
 llama_model_free(model);llama_backend_free();return 0;
}
