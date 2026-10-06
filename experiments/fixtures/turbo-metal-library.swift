import Foundation
import Metal
let device=MTLCreateSystemDefaultDevice()!
let source=try String(contentsOfFile:CommandLine.arguments[1],encoding:.utf8)
let options=MTLCompileOptions();options.languageVersion = .version3_0
let library=try device.makeLibrary(source:source,options:options)
let wanted=["kernel_flash_attn_ext_vec_kq8_0_vturbo3_dk256_dv256","kernel_flash_attn_ext_vec_kq8_0_vturbo4_dk256_dv256","kernel_turbo_wht"]
for name in wanted { precondition(library.functionNames.contains(name),"Missing \(name)") }
print(String(data:try JSONSerialization.data(withJSONObject:["device":device.name,"required_functions":wanted,"function_count":library.functionNames.count]),encoding:.utf8)!)
