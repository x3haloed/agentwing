#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <CommonCrypto/CommonDigest.h>
#include <simd/simd.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <errno.h>
#include <sys/resource.h>

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
 if(argc!=5)fail(@"usage: expert_overlap model fixtures kernels output-dir");NSError*e=nil;
 NSArray*fixtures=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[2])] options:0 error:&e];if(fixtures.count!=72)fail(@"fixtures");
 id<MTLDevice>d=MTLCreateSystemDefaultDevice();id<MTLLibrary>lib=[d newLibraryWithSource:[NSString stringWithContentsOfFile:@(argv[3]) encoding:NSUTF8StringEncoding error:&e] options:nil error:&e];if(!lib)fail(e.description);
 id<MTLComputePipelineState>gemv=pipeline(d,lib,@"gemv_affine_fast8"),silu=pipeline(d,lib,@"silu_mul");id<MTLCommandQueue>queue=[d newCommandQueue];
 NSMutableArray*ws=[NSMutableArray array],*ys=[NSMutableArray array];for(int k=0;k<8;k++){id<MTLBuffer>w=[d newBufferWithLength:3342336 options:MTLResourceStorageModeShared],y=[d newBufferWithLength:14336 options:MTLResourceStorageModeShared];if(!w||!y)fail(@"allocation");[ws addObject:w];[ys addObject:y];}
 id<MTLBuffer>x=[d newBufferWithLength:8192 options:MTLResourceStorageModeShared];if(!x)fail(@"allocation");int fds[40];for(int l=0;l<40;l++)fds[l]=-1;
 // Interleaved C/A/C/A/C; timing excludes hashes, verification and fixture setup.
 for(int arm=0;arm<5;arm++){BOOL overlap=arm%2;NSUInteger fixture=0;double seconds=0;struct rusage before,after;getrusage(RUSAGE_SELF,&before);
 for(NSDictionary*r in fixtures){@autoreleasepool{
 NSUInteger layer=[r[@"layer"] unsignedIntegerValue];NSArray*input=r[@"input_f32_bits"],*experts=r[@"experts"];if(layer>=40||input.count!=2048||experts.count!=8)fail(@"shape");for(int i=0;i<2048;i++)((uint32_t*)x.contents)[i]=[input[i] unsignedIntValue];
 if(fds[layer]<0){fds[layer]=open([NSString stringWithFormat:@"%s/packed_experts/layer_%02lu.bin",argv[1],layer].UTF8String,O_RDONLY);if(fds[layer]<0)fail(@"open");}
 int fd=fds[layer];NSMutableArray*ready=[NSMutableArray array];for(int k=0;k<8;k++)[ready addObject:dispatch_semaphore_create(0)];dispatch_group_t reads=dispatch_group_create();
 double start=NSProcessInfo.processInfo.systemUptime;
 for(int k=0;k<8;k++){NSUInteger expert=[experts[k] unsignedIntegerValue];if(expert>=256)fail(@"expert");id<MTLBuffer>w=ws[k];dispatch_semaphore_t sem=ready[k];dispatch_group_async(reads,dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0),^{size_t done=0;while(done<3342336){ssize_t n=pread(fd,(char*)w.contents+done,3342336-done,expert*3342336+done);if(n<0&&errno==EINTR)continue;if(n<=0)fail(@"read");done+=n;}dispatch_semaphore_signal(sem);});}
 if(!overlap)dispatch_group_wait(reads,DISPATCH_TIME_FOREVER);
 NSMutableArray*cbs=[NSMutableArray array];id<MTLCommandBuffer>cb=nil;id<MTLComputeCommandEncoder>enc=nil;
 if(!overlap){cb=[queue commandBuffer];enc=[cb computeCommandEncoder];}
 for(int k=0;k<8;k++){
 if(overlap){dispatch_semaphore_wait(ready[k],DISPATCH_TIME_FOREVER);cb=[queue commandBuffer];enc=[cb computeCommandEncoder];}
 id<MTLBuffer>w=ws[k],y=ys[k];Gemv gate={0,1048576,1081344,512,2048,64,8,2,0,0},up={1114112,2162688,2195456,512,2048,64,8,2,512,0},down={2228224,3276800,3309568,2048,512,64,8,2,1536,1024};
 encode(enc,gemv,w,x,y,gate);encode(enc,gemv,w,x,y,up);[enc memoryBarrierWithScope:MTLBarrierScopeBuffers];[enc setComputePipelineState:silu];for(int j=0;j<3;j++)[enc setBuffer:y offset:0 atIndex:j];vector_uint4 po={512,0,512,1024};[enc setBytes:&po length:sizeof po atIndex:3];[enc dispatchThreads:MTLSizeMake(512,1,1) threadsPerThreadgroup:MTLSizeMake(64,1,1)];[enc memoryBarrierWithScope:MTLBarrierScopeBuffers];encode(enc,gemv,w,y,y,down);
 if(overlap){[enc endEncoding];[cb commit];[cbs addObject:cb];}
 }
 if(!overlap){[enc endEncoding];[cb commit];[cbs addObject:cb];}
 for(id<MTLCommandBuffer>b in cbs){[b waitUntilCompleted];if(b.status!=MTLCommandBufferStatusCompleted)fail(b.error.description);}dispatch_group_wait(reads,DISPATCH_TIME_FOREVER);seconds+=NSProcessInfo.processInfo.systemUptime-start;
 NSMutableArray*hashes=[NSMutableArray array];for(int k=0;k<8;k++){id<MTLBuffer>y=ys[k];for(int j=0;j<3584;j++)if(!isfinite(((float*)y.contents)[j]))fail(@"nonfinite");[hashes addObject:hash(y.contents,y.length)];}
 NSDictionary*row=@{@"arm":@(arm),@"overlap":@(overlap),@"fixture":@(fixture++),@"stages_sha256":hashes};puts([[NSString alloc]initWithData:[NSJSONSerialization dataWithJSONObject:row options:NSJSONWritingSortedKeys error:&e] encoding:NSUTF8StringEncoding].UTF8String);
 }}getrusage(RUSAGE_SELF,&after);fprintf(stderr,"arm=%d overlap=%d seconds=%.9f inblock=%ld\n",arm,overlap,seconds,after.ru_inblock-before.ru_inblock);fflush(stdout);
 }for(int l=0;l<40;l++)if(fds[l]>=0)close(fds[l]);return 0;
}}
