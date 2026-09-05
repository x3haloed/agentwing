#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <libproc.h>
#include <sys/resource.h>
#include <sys/mman.h>
#include <sys/sysctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9; }
static struct rusage_info_v4 usage(void) { struct rusage_info_v4 r={0};if(proc_pid_rusage(getpid(),RUSAGE_INFO_V4,(rusage_info_t *)&r))abort();return r; }
static void checkHost(void) { int pressure=0;size_t n=sizeof pressure;if(sysctlbyname("kern.memorystatus_vm_pressure_level",&pressure,&n,NULL,0)||pressure>=4)abort(); }
static void fail(NSString *s) { fprintf(stderr,"%s\n",s.UTF8String);exit(1); }
int main(int argc,const char **argv) { @autoreleasepool {
 if(argc<2||argc>3)fail(@"usage: expert_mapping packed_experts/layer_00.bin [churn]");
 const NSUInteger workingGroups=(argc==3 && strcmp(argv[2],"churn")==0) ? 16 : 8;
 const NSUInteger stride=3342336,batch=8,words=stride/4,groups=words/256,rounds=16;
 if(stride%getpagesize())fail(@"stride is not page aligned");
 int fd=open(argv[1],O_RDONLY);if(fd<0)fail(@"open failed");
 id<MTLDevice> dev=MTLCreateSystemDefaultDevice();if(!dev)fail(@"no Metal device");
 NSError *error=nil;
 NSString *src=@"#include <metal_stdlib>\nusing namespace metal; kernel void scan(device const uint *x [[buffer(0)]],device uint *y [[buffer(1)]],uint i [[thread_position_in_grid]]) { uint a=0; for(uint k=0;k<256;k++){uint v=x[i*256+k]; a=(a<<5 | a>>27)^v;} y[i]=a;}";
 id<MTLLibrary> lib=[dev newLibraryWithSource:src options:nil error:&error];if(!lib)fail(error.description);
 id<MTLComputePipelineState> pipeline=[dev newComputePipelineStateWithFunction:[lib newFunctionWithName:@"scan"] error:&error];if(!pipeline)fail(error.description);
 id<MTLCommandQueue> queue=[dev newCommandQueue];
 NSMutableArray<id<MTLBuffer>> *slots=[NSMutableArray array];
 for(NSUInteger j=0;j<batch;j++){id<MTLBuffer>b=[dev newBufferWithLength:stride options:MTLResourceStorageModeShared];if(!b)fail(@"allocation failed");[slots addObject:b];}
 id<MTLBuffer> out=[dev newBufferWithLength:batch*groups*4 options:MTLResourceStorageModeShared];
 NSMutableArray<NSData*> *reference=[NSMutableArray array];
 // Independently establish exact bytes and CPU-computed GPU scan expectations.
 double validationStart=now();
 for(NSUInteger r=0;r<workingGroups;r++){
  NSMutableData *expected=[NSMutableData dataWithLength:batch*groups*4];uint32_t *dst=expected.mutableBytes;
  for(NSUInteger j=0;j<batch;j++){
   off_t off=(r*batch+j)*stride;if(pread(fd,slots[j].contents,stride,off)!=stride)fail(@"validation read failed");
   void *mapped=mmap(NULL,stride,PROT_READ,MAP_PRIVATE,fd,off);if(mapped==MAP_FAILED)fail(@"validation map failed");
   if(memcmp(mapped,slots[j].contents,stride))fail(@"mapped bytes differ");munmap(mapped,stride);
   uint32_t *x=slots[j].contents;for(NSUInteger i=0;i<groups;i++){uint32_t a=0;for(NSUInteger k=0;k<256;k++)a=((a<<5)|(a>>27))^x[i*256+k];dst[j*groups+i]=a;}
  }
  [reference addObject:expected];
 }
 fprintf(stderr,"validated %lu experts byte-for-byte; CPU expectations computed; validation %.3fs; warm-cache diagnostic\n",(unsigned long)(workingGroups*batch),now()-validationStart);
 NSArray *arms=@[@"concurrent",@"mapped",@"retained-mapped",@"concurrent",@"retained-mapped",@"mapped",@"concurrent"];
 for(NSUInteger arm=0;arm<arms.count;arm++){
  NSString *mode=arms[arm];NSMutableDictionary<NSNumber*,id<MTLBuffer>> *held=[NSMutableDictionary dictionary];NSMutableArray<NSNumber*> *fifo=[NSMutableArray array];NSUInteger maxMappings=0;double start=now(),fetch=0,gpuWait=0,release=0,gpu=0;uint64_t peak=0;struct rusage_info_v4 before=usage();
  for(NSUInteger r=0;r<rounds;r++){@autoreleasepool{
   checkHost();double t=now();NSMutableArray<id<MTLBuffer>> *inputs=[NSMutableArray array];
   if([mode containsString:@"mapped"]){
    for(NSUInteger j=0;j<batch;j++){
     NSNumber *key=@((r%workingGroups)*batch+j);if(held[key]){[inputs addObject:held[key]];continue;}
     if([mode isEqual:@"retained-mapped"] && held.count==64){[held removeObjectForKey:fifo[0]];[fifo removeObjectAtIndex:0];}
     void *p=mmap(NULL,stride,PROT_READ,MAP_PRIVATE,fd,((r%workingGroups)*batch+j)*stride);if(p==MAP_FAILED)fail(@"mmap failed");
     id<MTLBuffer>b=[dev newBufferWithBytesNoCopy:p length:stride options:MTLResourceStorageModeShared deallocator:^(void *p,NSUInteger n){munmap(p,n);}];
     if(!b){munmap(p,stride);fail(@"GPU mapping rejected");}[inputs addObject:b];if([mode isEqual:@"retained-mapped"]){held[key]=b;[fifo addObject:key];}
    }
   } else {
    void (^readOne)(size_t)=^(size_t j){if(pread(fd,slots[j].contents,stride,((r%workingGroups)*batch+j)*stride)!=stride)abort();};
    if([mode isEqual:@"concurrent"])dispatch_apply(batch,dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0),readOne);else for(NSUInteger j=0;j<batch;j++)readOne(j);
    [inputs addObjectsFromArray:slots];
   }
   maxMappings=MAX(maxMappings,held.count ? held.count : ([mode isEqual:@"mapped"] ? batch : 0));
   fetch+=now()-t;
   id<MTLCommandBuffer> cb=[queue commandBuffer];id<MTLComputeCommandEncoder> enc=[cb computeCommandEncoder];[enc setComputePipelineState:pipeline];
   for(NSUInteger j=0;j<batch;j++){[enc setBuffer:inputs[j] offset:0 atIndex:0];[enc setBuffer:out offset:j*groups*4 atIndex:1];[enc dispatchThreads:MTLSizeMake(groups,1,1) threadsPerThreadgroup:MTLSizeMake(128,1,1)];}
   [enc endEncoding];t=now();[cb commit];[cb waitUntilCompleted];gpuWait+=now()-t;if(cb.status!=MTLCommandBufferStatusCompleted)fail(cb.error.description);gpu+=cb.GPUEndTime-cb.GPUStartTime;
   if(memcmp(out.contents,reference[r%workingGroups].bytes,batch*groups*4))fail(@"GPU result differs from CPU reference");
   struct rusage_info_v4 u=usage();peak=MAX(peak,u.ri_phys_footprint);
   t=now();[inputs removeAllObjects];enc=nil;cb=nil;release+=now()-t;
  }}
  double cleanup=now();[held removeAllObjects];release+=now()-cleanup;
  struct rusage_info_v4 after=usage();NSDictionary *result=@{@"arm":@(arm),@"working_experts":@(workingGroups*batch),@"mode":mode,@"rounds":@(rounds),@"max_live_mapping_bytes":@(maxMappings*stride),@"logical_bytes":@(rounds*batch*stride),@"wall_seconds":@(now()-start),@"fetch_seconds":@(fetch),@"gpu_wait_seconds":@(gpuWait),@"gpu_seconds":@(gpu),@"release_seconds":@(release),@"disk_read_bytes":@(after.ri_diskio_bytesread-before.ri_diskio_bytesread),@"pageins":@(after.ri_pageins-before.ri_pageins),@"raw_user_time":@(after.ri_user_time-before.ri_user_time),@"raw_system_time":@(after.ri_system_time-before.ri_system_time),@"peak_sampled_footprint_bytes":@(peak),@"end_footprint_bytes":@(after.ri_phys_footprint),@"gpu_results_match_cpu":@YES};
  NSData *json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:&error];puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);fflush(stdout);
 }
 close(fd);return 0;
}}
