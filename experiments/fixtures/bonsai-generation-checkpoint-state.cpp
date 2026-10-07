#include "llama.h"
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>
int main(int argc,char **argv) {
 if(argc!=5)return 2;
 std::ifstream f(argv[2],std::ios::binary);std::vector<llama_token> ids;llama_token id;
 while(f.read((char*)&id,4))ids.push_back(id);
 if(ids.size()!=660)return 3;
 ggml_backend_load_all_from_path(argv[4]);llama_backend_init();
 auto mp=llama_model_default_params();mp.n_gpu_layers=999;
 auto *m=llama_model_load_from_file(argv[1],mp);if(!m)return 4;
 for(int arm=0;arm<2;arm++) {
  auto cp=llama_context_default_params();cp.n_ctx=16384;cp.n_batch=256;cp.n_ubatch=128;cp.n_seq_max=1;cp.n_rs_seq=0;
  cp.type_k=GGML_TYPE_Q8_0;cp.type_v=GGML_TYPE_TURBO6_0;cp.flash_attn_type=LLAMA_FLASH_ATTN_TYPE_ENABLED;
  auto *c=llama_init_from_model(m,cp);if(!c)return 5;
  if(llama_decode(c,llama_batch_get_one(ids.data(),20)))return 6;
  std::vector<unsigned char> snapshot;
  const int end=arm?660:570;
  for(int j=20;j<end;j++) {
   if(llama_decode(c,llama_batch_get_one(ids.data()+j,1)))return 7;
   llama_synchronize(c);
   if(arm && j==530) {
    snapshot.resize(llama_state_seq_get_size_ext(c,0,LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY));
    if(llama_state_seq_get_data_ext(c,snapshot.data(),snapshot.size(),0,LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY)!=snapshot.size())return 8;
    printf("checkpoint_tokens=531 bytes=%zu\n",snapshot.size());fflush(stdout);
   }
  }
  if(arm) {
   if(llama_state_seq_set_data_ext(c,snapshot.data(),snapshot.size(),0,LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY)!=snapshot.size())return 9;
   if(!llama_memory_seq_rm(llama_get_memory(c),0,531,-1))return 10;
   for(int j=531;j<570;j++)if(llama_decode(c,llama_batch_get_one(ids.data()+j,1)))return 11;
  }
  auto *logits=llama_get_logits_ith(c,-1);const int n=llama_vocab_n_tokens(llama_model_get_vocab(m));
  std::string p=std::string(argv[3])+"/"+(arm?"restored":"control")+".f32";FILE *out=fopen(p.c_str(),"wb");
  if(!out||!logits||fwrite(logits,4,n,out)!=(size_t)n)return 12;fclose(out);
  printf("arm=%d target_tokens=570 vocab=%d\n",arm,n);fflush(stdout);llama_free(c);
 }
 llama_model_free(m);llama_backend_free();return 0;
}
