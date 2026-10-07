#include "llama.h"
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>
static int dump(llama_context *c,llama_model *m,const std::string &p) {
 auto *l=llama_get_logits_ith(c,-1);int n=llama_vocab_n_tokens(llama_model_get_vocab(m));FILE *f=fopen(p.c_str(),"wb");
 if(!f||!l||fwrite(l,4,n,f)!=(size_t)n)return 1;fclose(f);return 0;
}
int main(int argc,char **argv) {
 if(argc!=5)return 2;std::ifstream f(argv[2],std::ios::binary);std::vector<llama_token> ids;llama_token id;while(f.read((char*)&id,4))ids.push_back(id);if(ids.size()!=1735)return 3;
 ggml_backend_load_all_from_path(argv[4]);llama_backend_init();auto mp=llama_model_default_params();mp.n_gpu_layers=999;auto *m=llama_model_load_from_file(argv[1],mp);if(!m)return 4;
 auto cp=llama_context_default_params();cp.n_ctx=16384;cp.n_batch=256;cp.n_ubatch=128;cp.n_seq_max=1;cp.n_rs_seq=0;cp.type_k=GGML_TYPE_Q8_0;cp.type_v=GGML_TYPE_TURBO6_0;cp.flash_attn_type=LLAMA_FLASH_ATTN_TYPE_ENABLED;
 const std::vector<int> targets={1042,1043,1044,1554,1555,1556,1594};
 auto *c=llama_init_from_model(m,cp);if(!c)return 5;if(llama_decode(c,llama_batch_get_one(ids.data(),20)))return 6;
 std::vector<std::pair<int,std::vector<unsigned char>>> snapshots;
 for(int j=20;j<1735;j++) {
  if(llama_decode(c,llama_batch_get_one(ids.data()+j,1)))return 7;llama_synchronize(c);
  if(std::find(targets.begin(),targets.end(),j+1)!=targets.end())if(dump(c,m,std::string(argv[3])+"/"+std::to_string(j+1)+"-control.f32"))return 8;
  if((j+1)==531||(j+1)==1043||(j+1)==1555) {
   if(snapshots.size()==2)snapshots.erase(snapshots.begin());
   std::vector<unsigned char> b(llama_state_seq_get_size_ext(c,0,LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY));if(llama_state_seq_get_data_ext(c,b.data(),b.size(),0,LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY)!=b.size())return 9;
   snapshots.emplace_back(j+1,std::move(b));
  }
 }
 // Keep the original KV suffix in a full-state snapshot for independent cases.
 std::vector<unsigned char> full(llama_state_seq_get_size_ext(c,0,0));if(llama_state_seq_get_data_ext(c,full.data(),full.size(),0,0)!=full.size())return 10;
 for(int target:targets) {
  if(llama_state_seq_set_data_ext(c,full.data(),full.size(),0,0)!=full.size())return 11;
  int restored=0;
  for(auto it=snapshots.rbegin();it!=snapshots.rend();++it)if(it->first<target) {
   if(llama_state_seq_set_data_ext(c,it->second.data(),it->second.size(),0,LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY)!=it->second.size())return 12;
   restored=it->first;break;
  }
  if(restored) {if(!llama_memory_seq_rm(llama_get_memory(c),0,restored,-1))return 13;}
  else {llama_memory_clear(llama_get_memory(c),true);if(llama_decode(c,llama_batch_get_one(ids.data(),20)))return 14;restored=20;}
  for(int j=restored;j<target;j++)if(llama_decode(c,llama_batch_get_one(ids.data()+j,1)))return 15;
  if(dump(c,m,std::string(argv[3])+"/"+std::to_string(target)+"-restored.f32"))return 16;
  printf("target=%d restored=%d retained=2\n",target,restored);fflush(stdout);
 }
 llama_free(c);llama_model_free(m);llama_backend_free();return 0;
}
