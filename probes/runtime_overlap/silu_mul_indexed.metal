// AW-0043: original SwiGLU arithmetic, arbitrary token/pick offsets.
// Each uint4 is (count, gate offset, up offset, destination offset).
kernel void silu_mul_indexed(
    device const float *g [[buffer(0)]],
    device const float *u [[buffer(1)]],
    device float *h [[buffer(2)]],
    constant uint4 *slots [[buffer(3)]],
    uint2 tpg [[thread_position_in_grid]])
{
    const uint4 po = slots[tpg.y];
    const uint i = tpg.x;
    if (i >= po.x) return;
    float gv = g[po.y + i];
    h[po.w + i] = (gv / (1.0f + metal::exp(-gv))) * u[po.z + i];
}
