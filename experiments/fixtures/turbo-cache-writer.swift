import Foundation
import Metal
let root=CommandLine.arguments[2], device=MTLCreateSystemDefaultDevice()!
let options=MTLCompileOptions();options.languageVersion = .version3_0
let library=try device.makeLibrary(source:String(contentsOfFile:CommandLine.arguments[1],encoding:.utf8),options:options)
let queue=device.makeCommandQueue()!
func buffer(_ path:String)throws->MTLBuffer {let d=try Data(contentsOf:URL(fileURLWithPath:path));return d.withUnsafeBytes{device.makeBuffer(bytes:$0.baseAddress!,length:d.count,options:.storageModeShared)!}}
for bits in [3,4] {
 let pipeline=try device.makeComputePipelineState(function:library.makeFunction(name:"kernel_set_rows_f32_i64_turbo\(bits)")!)
 for layer in [3,31,63] {
  let dir="\(root)/\(layer)-\(bits)", size=bits==3 ? 100:136
  let args=try Data(contentsOf:URL(fileURLWithPath:dir+"/args.bin")),input=try buffer(dir+"/input.bin"),indices=try buffer(dir+"/indices.bin")
  let out=device.makeBuffer(length:192*size+512,options:.storageModeShared)!
  memset(out.contents(),0xa5,out.length)
  let command=queue.makeCommandBuffer()!,encoder=command.makeComputeCommandEncoder()!
  encoder.setComputePipelineState(pipeline);args.withUnsafeBytes{encoder.setBytes($0.baseAddress!,length:args.count,index:0)}
  encoder.setBuffer(input,offset:0,index:1);encoder.setBuffer(indices,offset:0,index:2);encoder.setBuffer(out,offset:256,index:3)
  encoder.dispatchThreadgroups(MTLSize(width:192,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:32,height:1,depth:1))
  encoder.endEncoding();command.commit();command.waitUntilCompleted();precondition(command.status == .completed)
  try Data(bytes:out.contents(),count:out.length).write(to:URL(fileURLWithPath:dir+"/output.bin"))
 }
}
print(device.name)
