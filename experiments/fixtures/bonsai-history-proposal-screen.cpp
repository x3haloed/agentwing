#include "llama.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <fstream>
#include <unordered_map>
#include <string>
#include <vector>
using llama_tokens=std::vector<llama_token>;
struct common_ngram_simple_config{uint16_t size_ngram;uint16_t size_mgram;};
#define LOG_DBG(...) ((void)0)
llama_tokens common_ngram_simple_draft(
        const common_ngram_simple_config & config,
        const llama_tokens & tokens, llama_token sampled) {

    // Simple implementation of self-speculative decoding without a draft model.
    //
    const size_t cur_len = tokens.size();

    const size_t n_draft_min = config.size_ngram; // size of n-gram to lookup in token history
    const size_t n_draft_max = config.size_mgram; // the m-gram following the found n-gram is used for draft

    // vector for tokens we want to verify.
    // return empty vector if there is no match.
    llama_tokens draft_tokens;

    // We need at least n_draft_min + n_draft_max + 1 tokens.
    if (cur_len <= static_cast<size_t>(n_draft_min + n_draft_max + 1)) {
        return draft_tokens;
    }

    // pattern search
    llama_tokens pattern;
    pattern.reserve(n_draft_min);
    for (size_t j = cur_len - n_draft_min + 1; j < cur_len; ++j) {
        pattern.push_back(tokens[j]);
    }
    pattern.push_back(sampled); // add the last token to the pattern

    size_t match_pos = 0; // we ignore position 0, position 0 == no match
                          // search backwards, but skip the current match (we are currently there)
    for (size_t j = cur_len - n_draft_min - 1; j > 0; --j) {
        bool match = true;
        for (size_t k = 0; k < pattern.size(); ++k) {
            if (tokens[j + k] != pattern[k]) {
                match = false;
                break;
            }
        }
        if (match) {
            match_pos = j;
            break;
        }
    }
    if (match_pos == 0) {
        return draft_tokens;
    }

    const size_t copy_max = std::min(
            n_draft_max,
            cur_len - (match_pos + n_draft_min)
            );
    if (copy_max < n_draft_min) {
        return draft_tokens;
    }
    LOG_DBG("%s: #tokens = %zu: found matching pattern at pos %zu, length %zu, draft length %zu\n",
            __func__, cur_len,
            match_pos, pattern.size(), copy_max);

    draft_tokens.reserve(copy_max);
    for (size_t j = 0; j < copy_max; ++j) {
        draft_tokens.push_back(tokens[match_pos + n_draft_min + j]);
    }
    return draft_tokens;
}

int main(int argc,char **argv){
 if(argc!=4)return 2;
 auto mp=llama_model_default_params();mp.vocab_only=true;mp.n_gpu_layers=0;
 auto *model=llama_model_load_from_file(argv[1],mp);if(!model)return 3;auto *v=llama_model_get_vocab(model);
 std::unordered_map<std::string,std::vector<llama_token>> map;
 for(int i=0;i<llama_vocab_n_tokens(v);i++){std::vector<char> b(256);int n=llama_token_to_piece(v,i,b.data(),b.size(),0,true);if(n<0){b.resize(-n);n=llama_token_to_piece(v,i,b.data(),b.size(),0,true);}if(n>0)map[std::string(b.data(),n)].push_back(i);}
 std::ifstream input(argv[2],std::ios::binary);llama_tokens ids;int missing=0,ambiguous=0;uint32_t n;
 while(input.read((char*)&n,4)){assert(n<1048576);std::string piece(n,'\0');input.read(piece.data(),n);assert(input);auto found=map.find(piece);if(found==map.end())missing++;else if(found->second.size()!=1)ambiguous++;else ids.push_back(found->second[0]);}
 printf("pieces_unique=%zu missing=%d ambiguous=%d\n",ids.size(),missing,ambiguous);
 if(missing||ambiguous){llama_model_free(model);return 4;}
 std::ifstream initial(argv[3],std::ios::binary);llama_tokens history;llama_token token;while(initial.read((char*)&token,4))history.push_back(token);
 size_t i=0,passes=0,calls=0,proposed=0,accepted=0,rejected=0;
 while(i+1<ids.size()){
 auto draft=common_ngram_simple_draft({3,3},history,ids[i]);size_t k=0;
 while(k<draft.size() && i+1+k<ids.size() && draft[k]==ids[i+1+k])k++;
 if(!draft.empty()){calls++;proposed+=draft.size();accepted+=k;if(k<draft.size())rejected++;}
 size_t advance=std::min(k+1,ids.size()-1-i);for(size_t j=0;j<advance;j++)history.push_back(ids[i+j]);i+=advance;passes++;
 }
 printf("baseline_steps=%zu verification_passes=%zu draft_calls=%zu proposed=%zu oracle_accepted=%zu rejection_batches=%zu ideal_equal_pass_ratio=%.6f\n",ids.size()-1,passes,calls,proposed,accepted,rejected,double(ids.size()-1)/passes);
 llama_model_free(model);return 0;
}
