#import <Foundation/Foundation.h>
#include <libproc.h>
#include <sys/resource.h>
#include <unistd.h>
#include <stdlib.h>
int main(int argc,const char **argv) {
 if(argc!=2)return 2;int pid=atoi(argv[1]);if(pid<=1)return 2;
 while(1){@autoreleasepool{
  struct rusage_info_v4 r={0};if(proc_pid_rusage(pid,RUSAGE_INFO_V4,(rusage_info_t *)&r))return 0;
  printf("{\"uptime\":%.9f,\"disk_read_bytes\":%llu,\"disk_write_bytes\":%llu,\"pageins\":%llu,\"resident_bytes\":%llu,\"footprint_bytes\":%llu}\n",NSProcessInfo.processInfo.systemUptime,(unsigned long long)r.ri_diskio_bytesread,(unsigned long long)r.ri_diskio_byteswritten,(unsigned long long)r.ri_pageins,(unsigned long long)r.ri_resident_size,(unsigned long long)r.ri_phys_footprint);fflush(stdout);usleep(20000);
 }}
}
