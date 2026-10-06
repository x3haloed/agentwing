import Foundation
import Metal
struct Args { var nElements: Int64; var direction: Int32; var pad: Int32 = 0 }
let argv=CommandLine.arguments
let device=MTLCreateSystemDefaultDevice()!
let source=try String(contentsOfFile:argv[1],encoding:.utf8)
let library=try device.makeLibrary(source:source,options:nil)
let pipeline=try device.makeComputePipelineState(function:library.makeFunction(name:"kernel_turbo_wht")!)
let data=try Data(contentsOf:URL(fileURLWithPath:argv[2]))
precondition(data.count>0 && data.count%512==0)
let input=data.withUnsafeBytes { device.makeBuffer(bytes:$0.baseAddress!,length:data.count,options:.storageModeShared)! }
let output=device.makeBuffer(length:data.count,options:.storageModeShared)!
var args=Args(nElements:Int64(data.count/4),direction:Int32(argv[4])!)
let queue=device.makeCommandQueue()!, command=queue.makeCommandBuffer()!, encoder=command.makeComputeCommandEncoder()!
encoder.setComputePipelineState(pipeline)
encoder.setBytes(&args,length:MemoryLayout<Args>.stride,index:0)
encoder.setBuffer(input,offset:0,index:1);encoder.setBuffer(output,offset:0,index:2)
let groups=data.count/512
encoder.dispatchThreadgroups(MTLSize(width:(groups+63)/64,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:64,height:1,depth:1))
encoder.endEncoding();command.commit();command.waitUntilCompleted()
precondition(command.status == .completed,"Metal command failed")
try Data(bytes:output.contents(),count:data.count).write(to:URL(fileURLWithPath:argv[3]))
print(device.name)
