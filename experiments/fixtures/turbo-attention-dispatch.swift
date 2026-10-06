import Foundation
import Metal
let root=CommandLine.arguments[2], device=MTLCreateSystemDefaultDevice()!
let options=MTLCompileOptions();options.languageVersion = .version3_0
let library=try device.makeLibrary(source:String(contentsOfFile:CommandLine.arguments[1],encoding:.utf8),options:options)
let queue=device.makeCommandQueue()!
func buffer(_ path:String)throws->MTLBuffer { let d=try Data(contentsOf:URL(fileURLWithPath:path));return d.withUnsafeBytes{device.makeBuffer(bytes:$0.baseAddress!,length:d.count,options:.storageModeShared)!} }
for bits in [3,4] {
 let constants=MTLFunctionConstantValues()
 for i in 0...4 {var b=i==0;constants.setConstantValue(&b,type:.bool,index:400+i)}
 for (i,x) in [(420,8),(421,2),(422,4),(423,1)] {var v=Int32(x);constants.setConstantValue(&v,type:.int,index:i)}
 let function=try library.makeFunction(name:"kernel_flash_attn_ext_vec_kq8_0_vturbo\(bits)_dk256_dv256",constantValues:constants)
 let pipeline=try device.makeComputePipelineState(function:function)
 for layer in [3,31,63] {
  let dir="\(root)/\(layer)-\(bits)"
  let args=try Data(contentsOf:URL(fileURLWithPath:dir+"/args.bin"))
  let buffers=try ["q","k","v","mask"].map {try buffer(dir+"/\($0).bin")}
  let dummy=device.makeBuffer(length:4096,options:.storageModeShared)!,out=device.makeBuffer(length:6144*4,options:.storageModeShared)!
  let command=queue.makeCommandBuffer()!, encoder=command.makeComputeCommandEncoder()!
  encoder.setComputePipelineState(pipeline)
  args.withUnsafeBytes {encoder.setBytes($0.baseAddress!,length:args.count,index:0)}
  for (i,b) in buffers.enumerated(){encoder.setBuffer(b,offset:0,index:i+1)}
  encoder.setBuffer(dummy,offset:0,index:5);encoder.setBuffer(dummy,offset:0,index:6);encoder.setBuffer(out,offset:0,index:7)
  encoder.setThreadgroupMemoryLength(8192,index:0)
  encoder.dispatchThreadgroups(MTLSize(width:1,height:24,depth:1),threadsPerThreadgroup:MTLSize(width:32,height:4,depth:1))
  encoder.endEncoding();command.commit();command.waitUntilCompleted();precondition(command.status == .completed)
  try Data(bytes:out.contents(),count:6144*4).write(to:URL(fileURLWithPath:dir+"/output.bin"))
 }
}
print(device.name)
