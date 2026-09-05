#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <libproc.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
static void fail(NSString *s){fprintf(stderr,"%s\n",s.UTF8String);exit(1);}
static struct rusage_info_v4 usage(void){struct rusage_info_v4 r={0};if(proc_pid_rusage(getpid(),RUSAGE_INFO_V4,(rusage_info_t *)&r))abort();return r;}
int main(int argc,const char **argv){@autoreleasepool{
 if(argc!=3)fail(@"usage: real_route_transport model-dir batches.json");
 NSError *error=nil;NSArray *rows=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[2])] options:0 error:&error];if(!rows || rows.count!=1000)fail(@"invalid batches");
 const NSUInteger stride=3342336,groups=stride/4/256;NSUInteger maximum=0,total=0;
 for(NSDictionary *r in rows){NSArray *misses=r[@"misses"];maximum=MAX(maximum,misses.count);total+=misses.count;if([r[@"layer"] integerValue]<0 || [r[@"layer"] integerValue]>=40)fail(@"invalid layer");for(NSNumber *e in misses)if(e.integerValue<0||e.integerValue>=256)fail(@"invalid expert");}
 if(total!=9249)fail(@"unexpected miss count");int fds[40];for(int i=0;i<40;i++){NSString *path=[NSString stringWithFormat:@"%s/packed_experts/layer_%02d.bin",argv[1],i];fds[i]=open(path.UTF8String,O_RDONLY);if(fds[i]<0)fail(@"open failed");}
 id<MTLDevice> dev=MTLCreateSystemDefaultDevice();if(!dev)fail(@"no GPU");
 NSString *src=@"#include <metal_stdlib>\nusing namespace metal; kernel void scan(device const uint *x [[buffer(0)]],device uint *y [[buffer(1)]],uint i [[thread_position_in_grid]]) { uint a=0; for(uint k=0;k<256;k++){uint v=x[i*256+k]; a=(a<<5 | a>>27)^v;} y[i]=a;}";
 id<MTLLibrary> lib=[dev newLibraryWithSource:src options:nil error:&error];if(!lib)fail(error.description);
 id<MTLComputePipelineState> pipeline=[dev newComputePipelineStateWithFunction:[lib newFunctionWithName:@"scan"] error:&error];if(!pipeline)fail(error.description);
 id<MTLCommandQueue> queue=[dev newCommandQueue];NSMutableArray<id<MTLBuffer>> *slots=[NSMutableArray array];
 for(NSUInteger i=0;i<maximum;i++){id<MTLBuffer>b=[dev newBufferWithLength:stride options:MTLResourceStorageModeShared];if(!b)fail(@"allocation");[slots addObject:b];}
 id<MTLBuffer> out=[dev newBufferWithLength:maximum*groups*4 options:MTLResourceStorageModeShared];if(!out)fail(@"output allocation");
 NSMutableArray<NSData*> *reference=[NSMutableArray array];NSArray *widths=@[@0,@4,@0,@4,@0];
 for(NSUInteger arm=0;arm<widths.count;arm++){
  NSUInteger width=[widths[arm] unsignedIntegerValue];double start=now(),readSeconds=0,waitSeconds=0,gpuSeconds=0;struct rusage_info_v4 before=usage();uint64_t peak=0;NSUInteger index=0;
  for(NSDictionary *row in rows){@autoreleasepool{
   NSArray *misses=row[@"misses"];NSUInteger count=misses.count;int fd=fds[[row[@"layer"] intValue]];double t=now();
   // Strided workers bound in-flight preads without waiting for fixed waves.
   NSUInteger workers=width?MIN(width,count):count;
   dispatch_apply(workers,dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0),^(size_t w){for(NSUInteger j=w;j<count;j+=workers){size_t done=0;off_t base=[misses[j] unsignedLongLongValue]*stride;while(done<stride){ssize_t n=pread(fd,(char*)slots[j].contents+done,stride-done,base+done);if(n<0&&errno==EINTR)continue;if(n<=0)abort();done+=n;}}});
   readSeconds+=now()-t;
   if(count){id<MTLCommandBuffer> cb=[queue commandBuffer];id<MTLComputeCommandEncoder> enc=[cb computeCommandEncoder];[enc setComputePipelineState:pipeline];
    for(NSUInteger j=0;j<count;j++){[enc setBuffer:slots[j] offset:0 atIndex:0];[enc setBuffer:out offset:j*groups*4 atIndex:1];[enc dispatchThreads:MTLSizeMake(groups,1,1) threadsPerThreadgroup:MTLSizeMake(128,1,1)];}
    [enc endEncoding];t=now();[cb commit];[cb waitUntilCompleted];waitSeconds+=now()-t;if(cb.status!=MTLCommandBufferStatusCompleted)fail(cb.error.description);gpuSeconds+=cb.GPUEndTime-cb.GPUStartTime;
   }
   NSUInteger bytes=count*groups*4;if(arm==0)[reference addObject:[NSData dataWithBytes:out.contents length:bytes]];else if(reference[index].length!=bytes||memcmp(reference[index].bytes,out.contents,bytes))fail(@"scan mismatch");
   peak=MAX(peak,usage().ri_phys_footprint);index++;
  }}
  struct rusage_info_v4 after=usage();NSDictionary *result=@{@"arm":@(arm),@"concurrency":@(width),@"wall_seconds":@(now()-start),@"read_seconds":@(readSeconds),@"gpu_wait_seconds":@(waitSeconds),@"gpu_seconds":@(gpuSeconds),@"logical_bytes":@(total*stride),@"disk_read_bytes":@(after.ri_diskio_bytesread-before.ri_diskio_bytesread),@"pageins":@(after.ri_pageins-before.ri_pageins),@"peak_footprint_bytes":@(peak),@"buffer_bytes":@(maximum*stride),@"scan_matches_first_arm":@(arm>0)};
  NSData *json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:&error];puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);fflush(stdout);
 }
 for(int i=0;i<40;i++)close(fds[i]);return 0;
}}
