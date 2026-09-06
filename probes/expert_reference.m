#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <CommonCrypto/CommonDigest.h>
#include <simd/simd.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <errno.h>

typedef struct { uint64_t wOff,sOff,bOff;uint32_t outDim,inDim,groupSize,bits,scalesType,yOff,xOff; } Gemv;
_Static_assert(sizeof(Gemv)==56,"Gemv ABI");
static void fail(NSString*s){fprintf(stderr,"%s\n",s.UTF8String);exit(1);}
static NSString* hash(const void*p,NSUInteger n){unsigned char d[CC_SHA256_DIGEST_LENGTH];CC_SHA256(p,(CC_LONG)n,d);NSMutableString*s=[NSMutableString string];for(int i=0;i<CC_SHA256_DIGEST_LENGTH;i++)[s appendFormat:@"%02x",d[i]];return s;}
static float bf(const uint8_t*p){uint32_t bits=((uint32_t)p[0]|((uint32_t)p[1]<<8))<<16;float f;memcpy(&f,&bits,4);return f;}
static double error(const float*actual,const double*expected,NSUInteger n){double a=0,b=0;for(NSUInteger i=0;i<n;i++){if(!isfinite(actual[i])||!isfinite(expected[i]))fail(@"nonfinite reference");double d=actual[i]-expected[i];a+=d*d;b+=expected[i]*expected[i];}return sqrt(a/fmax(b,1e-30));}
static double projection(const uint8_t*blob,Gemv p,const float*x,const float*y){double expected[2048];for(uint32_t row=0;row<p.outDim;row++){double sum=0;for(uint32_t i=0;i<p.inDim;i++){uint32_t g=row*(p.inDim/64)+i/64;double scale=bf(blob+p.sOff+g*2),bias=bf(blob+p.bOff+g*2);sum+=(scale*blob[p.wOff+row*p.inDim+i]+bias)*(double)x[p.xOff+i];}expected[row]=sum;}return error(y+p.yOff,expected,p.outDim);}
static void encode(id<MTLComputeCommandEncoder>enc,id<MTLComputePipelineState>pipe,id<MTLBuffer>weights,id<MTLBuffer>x,id<MTLBuffer>y,Gemv p){[enc setComputePipelineState:pipe];[enc setBuffer:x offset:0 atIndex:0];for(int i=1;i<=3;i++)[enc setBuffer:weights offset:0 atIndex:i];[enc setBuffer:y offset:0 atIndex:4];[enc setBytes:&p length:sizeof p atIndex:5];[enc dispatchThreads:MTLSizeMake(32,p.outDim,1) threadsPerThreadgroup:MTLSizeMake(32,1,1)];}
static id<MTLComputePipelineState> pipeline(id<MTLDevice>d,id<MTLLibrary>lib,NSString*name){NSError*e=nil;id<MTLComputePipelineState>p=[d newComputePipelineStateWithFunction:[lib newFunctionWithName:name] error:&e];if(!p)fail(e.description);return p;}
int main(int argc,const char**argv){@autoreleasepool{
 if(argc!=5)fail(@"usage: expert_reference model-dir fixtures.json kernels.txt output-dir");NSError*e=nil;
 NSArray*fixtures=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[2])] options:0 error:&e];if(fixtures.count!=72)fail(@"expected 72 fixtures");
 NSString*source=[NSString stringWithContentsOfFile:@(argv[3]) encoding:NSUTF8StringEncoding error:&e];id<MTLDevice>d=MTLCreateSystemDefaultDevice();id<MTLLibrary>lib=[d newLibraryWithSource:source options:nil error:&e];if(!lib)fail(e.description);
 id<MTLComputePipelineState>gemv=pipeline(d,lib,@"gemv_affine_fast8"),silu=pipeline(d,lib,@"silu_mul"),accum=pipeline(d,lib,@"weighted_accum");id<MTLCommandQueue>queue=[d newCommandQueue];
 const NSUInteger stride=3342336,D=2048,interWidth=512,N=3*interWidth+D;
 id<MTLBuffer>w=[d newBufferWithLength:stride options:MTLResourceStorageModeShared],x=[d newBufferWithLength:D*4 options:MTLResourceStorageModeShared],y=[d newBufferWithLength:N*4 options:MTLResourceStorageModeShared],mixdata=[d newBufferWithLength:(9*D+1)*4 options:MTLResourceStorageModeShared],mixture=[d newBufferWithLength:D*4 options:MTLResourceStorageModeShared];if(!w||!x||!y||!mixdata||!mixture)fail(@"allocation");
 int fds[40];for(int l=0;l<40;l++)fds[l]=-1;
 double maxProjection=0,maxActivation=0,maxMixture=0;NSUInteger count=0;
 for(NSDictionary*r in fixtures){@autoreleasepool{
  NSUInteger layer=[r[@"layer"] unsignedIntegerValue];NSArray*input=r[@"input_f32_bits"],*experts=r[@"experts"],*weightBits=r[@"weights_f32_bits"];
  if(layer>=40||input.count!=D||experts.count!=8||weightBits.count!=8)fail(@"fixture shape");
  for(NSUInteger i=0;i<D;i++)((uint32_t*)x.contents)[i]=[input[i] unsignedIntValue];float weights[8];for(int k=0;k<8;k++){uint32_t b=[weightBits[k] unsignedIntValue];memcpy(&weights[k],&b,4);}
  if(fds[layer]<0){NSString*path=[NSString stringWithFormat:@"%s/packed_experts/layer_%02lu.bin",argv[1],layer];fds[layer]=open(path.UTF8String,O_RDONLY);if(fds[layer]<0)fail(@"expert open");}
  memset(mixdata.contents,0,mixdata.length);memset(mixture.contents,0,mixture.length);NSMutableArray*outputs=[NSMutableArray array];
  for(NSUInteger k=0;k<8;k++){@autoreleasepool{
   NSUInteger expert=[experts[k] unsignedIntegerValue];if(expert>=256)fail(@"expert id");size_t done=0;while(done<stride){ssize_t n=pread(fds[layer],(char*)w.contents+done,stride-done,expert*stride+done);if(n<0&&errno==EINTR)continue;if(n<=0)fail(@"expert read");done+=n;}
   Gemv gate={0,1048576,1081344,interWidth,D,64,8,2,0,0},up={1114112,2162688,2195456,interWidth,D,64,8,2,interWidth,0},down={2228224,3276800,3309568,D,interWidth,64,8,2,3*interWidth,2*interWidth};
   id<MTLCommandBuffer>cb=[queue commandBuffer];id<MTLComputeCommandEncoder>enc=[cb computeCommandEncoder];encode(enc,gemv,w,x,y,gate);encode(enc,gemv,w,x,y,up);[enc memoryBarrierWithScope:MTLBarrierScopeBuffers];
   [enc setComputePipelineState:silu];for(int j=0;j<3;j++)[enc setBuffer:y offset:0 atIndex:j];vector_uint4 po={(uint32_t)interWidth,0,(uint32_t)interWidth,(uint32_t)(2*interWidth)};[enc setBytes:&po length:sizeof po atIndex:3];[enc dispatchThreads:MTLSizeMake(interWidth,1,1) threadsPerThreadgroup:MTLSizeMake(64,1,1)];[enc memoryBarrierWithScope:MTLBarrierScopeBuffers];encode(enc,gemv,w,y,y,down);[enc endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.status!=MTLCommandBufferStatusCompleted)fail(cb.error.description);
   float*out=y.contents;double pe=fmax(projection(w.contents,gate,x.contents,out),fmax(projection(w.contents,up,x.contents,out),projection(w.contents,down,out,out)));double expected[512];for(NSUInteger i=0;i<interWidth;i++)expected[i]=((double)out[i]/(1+exp(-(double)out[i])))*out[interWidth+i];double ae=error(out+2*interWidth,expected,interWidth);maxProjection=fmax(maxProjection,pe);maxActivation=fmax(maxActivation,ae);
   if(pe>1e-4||ae>1e-4)fail([NSString stringWithFormat:@"reference discrepancy fixture=%lu expert=%lu projection=%.9g activation=%.9g",count,expert,pe,ae]);
   memcpy((float*)mixdata.contents+k*D,out+3*interWidth,D*4);NSString*filename=[NSString stringWithFormat:@"fixture-%03lu-expert-%03lu.f32",count,expert];NSString*path=[@(argv[4]) stringByAppendingPathComponent:filename];if(![[NSData dataWithBytes:out length:N*4] writeToFile:path options:NSDataWritingWithoutOverwriting error:&e])fail(e.description);
   [outputs addObject:@{@"expert":@(expert),@"source_sha256":hash(w.contents,stride),@"stages_file":filename,@"stages_sha256":hash(out,N*4),@"projection_relative_l2":@(pe),@"silu_relative_l2":@(ae)}];
  }}
  id<MTLCommandBuffer>cb=[queue commandBuffer];id<MTLComputeCommandEncoder>enc=[cb computeCommandEncoder];[enc setComputePipelineState:accum];[enc setBuffer:mixture offset:0 atIndex:0];[enc setBuffer:mixdata offset:0 atIndex:1];vector_uint8 ap={(uint32_t)D,8,0,(uint32_t)(8*D),(uint32_t)(9*D),0,0,0};[enc setBytes:&ap length:sizeof ap atIndex:2];[enc setBytes:weights length:sizeof weights atIndex:3];[enc dispatchThreads:MTLSizeMake(D,1,1) threadsPerThreadgroup:MTLSizeMake(64,1,1)];[enc endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.status!=MTLCommandBufferStatusCompleted)fail(cb.error.description);
  double expected[2048];for(NSUInteger i=0;i<D;i++){expected[i]=0;for(int k=0;k<8;k++)expected[i]+=(double)weights[k]*((float*)mixdata.contents)[k*D+i];}double me=error(mixture.contents,expected,D);maxMixture=fmax(maxMixture,me);if(me>1e-4)fail(@"mixture reference discrepancy");
  NSString*name=[NSString stringWithFormat:@"fixture-%03lu-mixture.f32",count];if(![[NSData dataWithBytes:mixture.contents length:D*4] writeToFile:[@(argv[4]) stringByAppendingPathComponent:name] options:NSDataWritingWithoutOverwriting error:&e])fail(e.description);
  NSDictionary*row=@{@"fixture":@(count),@"layer":@(layer),@"experts":outputs,@"mixture_file":name,@"mixture_sha256":hash(mixture.contents,D*4),@"mixture_relative_l2":@(me)};NSData*json=[NSJSONSerialization dataWithJSONObject:row options:NSJSONWritingSortedKeys error:&e];puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);fflush(stdout);count++;
 }}
 for(int l=0;l<40;l++)if(fds[l]>=0)close(fds[l]);fprintf(stderr,"fixtures=%lu max_projection=%.9g max_activation=%.9g max_mixture=%.9g\n",count,maxProjection,maxActivation,maxMixture);return 0;
}}
