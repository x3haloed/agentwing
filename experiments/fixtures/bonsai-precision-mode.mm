#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <fstream>
#include <vector>
#include <chrono>
#include <cstdio>
int main(int argc,char **argv){@autoreleasepool {
 if(argc!=9)return 2;
 NSString *source=[NSString stringWithContentsOfFile:@(argv[1]) encoding:NSUTF8StringEncoding error:nil];
 id<MTLDevice> dev=MTLCreateSystemDefaultDevice();NSError *err=nil;MTLCompileOptions *opts=[MTLCompileOptions new];opts.fastMathEnabled=atoi(argv[7])!=0;
 auto start=std::chrono::steady_clock::now();id<MTLLibrary> lib=[dev newLibraryWithSource:source options:opts error:&err];if(!lib){fprintf(stderr,"%s\n",err.description.UTF8String);return 3;}
 id<MTLComputePipelineState> enc=[dev newComputePipelineStateWithFunction:[lib newFunctionWithName:@"encode_values"] error:&err];
 id<MTLComputePipelineState> dec=[dev newComputePipelineStateWithFunction:[lib newFunctionWithName:@"decode_values"] error:&err];if(!enc||!dec)return 4;
 printf("compile_seconds=%.9f device=%s\n",std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count(),dev.name.UTF8String);
 unsigned bits=atoi(argv[2]),groups=384,size=4+16*bits;std::vector<float> values(groups*128);std::ifstream input(argv[3],std::ios::binary);input.read((char*)values.data(),values.size()*4);if(input.gcount()!=values.size()*4)return 5;
 std::vector<float> tables((1<<bits)*2-1);std::ifstream table(argv[4],std::ios::binary);table.read((char*)tables.data(),tables.size()*4);if(table.gcount()!=tables.size()*4)return 6;
 auto src=[dev newBufferWithBytes:values.data() length:values.size()*4 options:MTLResourceStorageModeShared];auto book=[dev newBufferWithBytes:tables.data() length:tables.size()*4 options:MTLResourceStorageModeShared];auto packed=[dev newBufferWithLength:groups*size options:MTLResourceStorageModeShared];auto out=[dev newBufferWithLength:values.size()*4 options:MTLResourceStorageModeShared];auto trace=[dev newBufferWithLength:values.size()*4 options:MTLResourceStorageModeShared];auto queue=[dev newCommandQueue];
 for(int w=0;w<5;w++){start=std::chrono::steady_clock::now();for(int r=0;r<64;r++){
 auto cmd=[queue commandBuffer];auto e=[cmd computeCommandEncoder];[e setComputePipelineState:enc];[e setBuffer:src offset:0 atIndex:0];[e setBuffer:book offset:0 atIndex:1];[e setBuffer:packed offset:0 atIndex:2];[e setBytes:&bits length:4 atIndex:3];[e setBuffer:trace offset:0 atIndex:4];[e dispatchThreads:MTLSizeMake(groups,1,1) threadsPerThreadgroup:MTLSizeMake(32,1,1)];[e endEncoding];
 e=[cmd computeCommandEncoder];[e setComputePipelineState:dec];[e setBuffer:packed offset:0 atIndex:0];[e setBuffer:book offset:0 atIndex:1];[e setBuffer:out offset:0 atIndex:2];[e setBytes:&bits length:4 atIndex:3];[e dispatchThreads:MTLSizeMake(groups,1,1) threadsPerThreadgroup:MTLSizeMake(32,1,1)];[e endEncoding];[cmd commit];[cmd waitUntilCompleted];if(cmd.status!=MTLCommandBufferStatusCompleted)return 7;
 // Touch every result after completion to include CPU readback.
 volatile unsigned char checksum=0;for(unsigned i=0;i<groups*size;i++)checksum^=((unsigned char*)packed.contents)[i];
 }printf("window=%d encode_decode_readback_seconds=%.9f\n",w,std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());fflush(stdout);}
 std::ofstream p(argv[5],std::ios::binary);p.write((char*)packed.contents,groups*size);std::ofstream o(argv[6],std::ios::binary);o.write((char*)out.contents,values.size()*4);
 std::ofstream tr(argv[8],std::ios::binary);tr.write((char*)trace.contents,values.size()*4);
 return 0;
}}
