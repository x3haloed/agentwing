#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <vector>
using llama_token=int32_t;
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

llama_tokens load(const char *p){std::ifstream f(p,std::ios::binary);llama_tokens v;llama_token t;while(f.read((char*)&t,4))v.push_back(t);return v;}
int main(int argc,char **argv){if(argc!=5)return 2;int n=std::atoi(argv[3]),m=std::atoi(argv[4]);if(n<1||n>32||m<1||m>32)return 4;auto ids=load(argv[1]);auto history=load(argv[2]);if(ids.size()<2||history.empty())return 3;
 size_t i=0,passes=0,calls=0,proposed=0,accepted=0,rejected=0;
 while(i+1<ids.size()){
 auto draft=common_ngram_simple_draft({uint16_t(n),uint16_t(m)},history,ids[i]);size_t k=0;
 while(k<draft.size() && i+1+k<ids.size() && draft[k]==ids[i+1+k])k++;
 if(!draft.empty()){calls++;proposed+=draft.size();accepted+=k;if(k<draft.size())rejected++;}
 size_t advance=std::min(k+1,ids.size()-1-i);for(size_t j=0;j<advance;j++)history.push_back(ids[i+j]);i+=advance;passes++;
 }
 printf("baseline_steps=%zu verification_passes=%zu draft_calls=%zu proposed=%zu oracle_accepted=%zu rejection_batches=%zu ideal_equal_pass_ratio=%.6f\n",ids.size()-1,passes,calls,proposed,accepted,rejected,double(ids.size()-1)/passes);return 0;}
