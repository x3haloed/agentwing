import Foundation
import Metal
let root=CommandLine.arguments[2], device=MTLCreateSystemDefaultDevice()!
let options=MTLCompileOptions();options.languageVersion = .version3_0
let library=try device.makeLibrary(source:String(contentsOfFile:CommandLine.arguments[1],encoding:.utf8),options:options)
struct WhtArgs {var elements:Int64=6144;var direction:Int32=1;var padding:Int32=0}
let inversePipeline=try device.makeComputePipelineState(function:library.makeFunction(name:"kernel_turbo_wht")!)
let queue=device.makeCommandQueue()!
func buffer(_ path:String)throws->MTLBuffer { let d=try Data(contentsOf:URL(fileURLWithPath:path));return d.withUnsafeBytes{device.makeBuffer(bytes:$0.baseAddress!,length:d.count,options:.storageModeShared)!} }
for bits in [3,4] {
 let constants=MTLFunctionConstantValues()
 for i in 0...4 {var b=i==0;constants.setConstantValue(&b,type:.bool,index:400+i)}
 for (i,x) in [(420,8),(421,2),(422,4),(423,1)] {var v=Int32(x);constants.setConstantValue(&v,type:.int,index:i)}
 let function=try library.makeFunction(name:"kernel_flash_attn_ext_vec_kq8_0_vturbo\(bits)_dk256_dv256",constantValues:constants)
 let pipeline=try device.makeComputePipelineState(function:function)
 let writer=try device.makeComputePipelineState(function:library.makeFunction(name:"kernel_set_rows_f32_i64_turbo\(bits)")!)
 for layer in [3,31,63] {
  let dir="\(root)/\(layer)-\(bits)"
  let args=try Data(contentsOf:URL(fileURLWithPath:dir+"/args.bin"))
  let buffers=try ["q","k","v","mask"].map {try buffer(dir+"/\($0).bin")}
  let dummy=device.makeBuffer(length:4096,options:.storageModeShared)!,out=device.makeBuffer(length:6144*4,options:.storageModeShared)!
  let command=queue.makeCommandBuffer()!
  let writeArgs=try Data(contentsOf:URL(fileURLWithPath:dir+"/writer-args.bin"))
  let values=try buffer(dir+"/values.bin"),indices=try buffer(dir+"/indices.bin")
  memset(buffers[2].contents(),0,buffers[2].length)
  let writeEncoder=command.makeComputeCommandEncoder()!
  writeEncoder.setComputePipelineState(writer)
  writeArgs.withUnsafeBytes{writeEncoder.setBytes($0.baseAddress!,length:writeArgs.count,index:0)}
  writeEncoder.setBuffer(values,offset:0,index:1);writeEncoder.setBuffer(indices,offset:0,index:2);writeEncoder.setBuffer(buffers[2],offset:0,index:3)
  writeEncoder.dispatchThreadgroups(MTLSize(width:192,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:32,height:1,depth:1));writeEncoder.endEncoding()
  let encoder=command.makeComputeCommandEncoder()!
  encoder.setComputePipelineState(pipeline)
  args.withUnsafeBytes {encoder.setBytes($0.baseAddress!,length:args.count,index:0)}
  for (i,b) in buffers.enumerated(){encoder.setBuffer(b,offset:0,index:i+1)}
  encoder.setBuffer(dummy,offset:0,index:5);encoder.setBuffer(dummy,offset:0,index:6);encoder.setBuffer(out,offset:0,index:7)
  encoder.setThreadgroupMemoryLength(8192,index:0)
  encoder.dispatchThreadgroups(MTLSize(width:1,height:24,depth:1),threadsPerThreadgroup:MTLSize(width:32,height:4,depth:1))
  encoder.endEncoding()
  let restored=device.makeBuffer(length:6144*4,options:.storageModeShared)!
  let inv=command.makeComputeCommandEncoder()!;inv.setComputePipelineState(inversePipeline)
  var wht=WhtArgs();inv.setBytes(&wht,length:MemoryLayout<WhtArgs>.stride,index:0)
  inv.setBuffer(out,offset:0,index:1);inv.setBuffer(restored,offset:0,index:2)
  inv.dispatchThreadgroups(MTLSize(width:1,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:64,height:1,depth:1));inv.endEncoding()
  command.commit();command.waitUntilCompleted();precondition(command.status == .completed)
  try Data(bytes:restored.contents(),count:6144*4).write(to:URL(fileURLWithPath:dir+"/restored.bin"))
  try Data(bytes:buffers[2].contents(),count:buffers[2].length).write(to:URL(fileURLWithPath:dir+"/written-cache.bin"))
  try Data(bytes:out.contents(),count:6144*4).write(to:URL(fileURLWithPath:dir+"/output.bin"))
 }
}
print(device.name)
