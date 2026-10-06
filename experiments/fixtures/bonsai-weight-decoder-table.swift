import Foundation
import Metal
struct Args { var blocks: UInt32; var rows: UInt32 }
let av=CommandLine.arguments
precondition(av.count==7)
let device=MTLCreateSystemDefaultDevice()!
let library=try device.makeLibrary(source:String(contentsOfFile:av[1],encoding:.utf8),options:nil)
let apply=try device.makeComputePipelineState(function:library.makeFunction(name:"multiply")!)
let width=Int(av[5])!,rows=Int(av[6])!;precondition(width>0 && width%128==0 && rows>0)
let weights=try Data(contentsOf:URL(fileURLWithPath:av[2])),input=try Data(contentsOf:URL(fileURLWithPath:av[3]))
precondition(weights.count==rows*(width/128)*28 && input.count==width*4)
let w=weights.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:weights.count,options:.storageModeShared)! }
let x=input.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:input.count,options:.storageModeShared)! }
let output=device.makeBuffer(length:rows*4,options:.storageModeShared)!
let queue=device.makeCommandQueue()!;var args=Args(blocks:UInt32(width/128),rows:UInt32(rows))
for i in 0..<5 {
 let start=DispatchTime.now().uptimeNanoseconds
 let command=queue.makeCommandBuffer()!,encoder=command.makeComputeCommandEncoder()!
 encoder.setComputePipelineState(apply);encoder.setBuffer(w,offset:0,index:0);encoder.setBuffer(x,offset:0,index:1);encoder.setBuffer(output,offset:0,index:2);encoder.setBytes(&args,length:MemoryLayout<Args>.stride,index:3)
 encoder.dispatchThreadgroups(MTLSize(width:(rows+3)/4,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:32,height:1,depth:1))
 encoder.endEncoding();command.commit();command.waitUntilCompleted();precondition(command.status == .completed)
 let data=Data(bytes:output.contents(),count:rows*4)
 let seconds=Double(DispatchTime.now().uptimeNanoseconds-start)/1e9
 print(String(format:"iteration=%d build_multiply_readback_seconds=%.9f",i,seconds))
 if i==4 { try data.write(to:URL(fileURLWithPath:av[4])) }
}
print("decoder_bytes=5120 device=\(device.name)")
