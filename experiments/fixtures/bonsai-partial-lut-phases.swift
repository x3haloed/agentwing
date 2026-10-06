import Foundation
import Metal
struct Args { var blocks: UInt32; var rows: UInt32 }
let av=CommandLine.arguments
precondition(av.count==7)
let device=MTLCreateSystemDefaultDevice()!
let library=try device.makeLibrary(source:String(contentsOfFile:av[1],encoding:.utf8),options:nil)
let build=try device.makeComputePipelineState(function:library.makeFunction(name:"make_lut")!)
let apply=try device.makeComputePipelineState(function:library.makeFunction(name:"multiply_lut")!)
let width=Int(av[5])!,rows=Int(av[6])!;precondition(width>0 && width%128==0 && rows>0)
let weights=try Data(contentsOf:URL(fileURLWithPath:av[2])),input=try Data(contentsOf:URL(fileURLWithPath:av[3]))
precondition(weights.count==rows*(width/128)*28 && input.count==width*4)
let w=weights.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:weights.count,options:.storageModeShared)! }
let x=input.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:input.count,options:.storageModeShared)! }
let lut=device.makeBuffer(length:(width/128)*864*4,options:.storageModeShared)!
let output=device.makeBuffer(length:rows*4,options:.storageModeShared)!
let queue=device.makeCommandQueue()!;var args=Args(blocks:UInt32(width/128),rows:UInt32(rows))
for i in 0..<5 {
 let start=DispatchTime.now().uptimeNanoseconds
 let command=queue.makeCommandBuffer()!,encoder=command.makeComputeCommandEncoder()!
 encoder.setComputePipelineState(build);encoder.setBuffer(x,offset:0,index:0);encoder.setBuffer(lut,offset:0,index:1);encoder.setBytes(&args,length:MemoryLayout<Args>.stride,index:2)
 encoder.dispatchThreads(MTLSize(width:(width/128)*864,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:256,height:1,depth:1))
 encoder.endEncoding();command.commit();command.waitUntilCompleted();precondition(command.status == .completed)
 let buildWall=Double(DispatchTime.now().uptimeNanoseconds-start)/1e9
 let buildGPU=command.gpuEndTime-command.gpuStartTime
 let applyStart=DispatchTime.now().uptimeNanoseconds
 let application=queue.makeCommandBuffer()!,consumer=application.makeComputeCommandEncoder()!
 consumer.setComputePipelineState(apply);consumer.setBuffer(w,offset:0,index:0);consumer.setBuffer(x,offset:0,index:1);consumer.setBuffer(lut,offset:0,index:2);consumer.setBuffer(output,offset:0,index:3);consumer.setBytes(&args,length:MemoryLayout<Args>.stride,index:4)
 consumer.dispatchThreadgroups(MTLSize(width:(rows+3)/4,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:32,height:1,depth:1))
 consumer.endEncoding();application.commit();application.waitUntilCompleted();precondition(application.status == .completed)
 let data=Data(bytes:output.contents(),count:rows*4)
 let seconds=Double(DispatchTime.now().uptimeNanoseconds-start)/1e9
 let applyWall=Double(DispatchTime.now().uptimeNanoseconds-applyStart)/1e9
 let applyGPU=application.gpuEndTime-application.gpuStartTime
 print(String(format:"iteration=%d build_wall=%.9f build_gpu=%.9f apply_wall=%.9f apply_gpu=%.9f total_wall=%.9f",i,buildWall,buildGPU,applyWall,applyGPU,seconds))
 if i==4 { try data.write(to:URL(fileURLWithPath:av[4])) }
}
print("scratch_bytes=\(lut.length) device=\(device.name)")
