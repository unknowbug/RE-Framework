# 常见算法模式识别（汇编/字节码级）

> 用途: Lift 步骤5（语义折叠）识别算法；确认后写入 knowledge/discovered/algorithm-fingerprints.md。
> 模块: core（re-binary / re-code 使用）

## 校验类

### CRC32
- 多项式: `0xEDB88320`（reflected）/ `0x04C11DB7`（normal）
- 初始值: `0xFFFFFFFF`，输出 XOR `0xFFFFFFFF`
- 特征: 256 项 uint32 查找表 + 每轮 `crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)`
- 汇编特征: `xor edx,edx` + `mov dl,[rcx+rax]` + `xor edx,esi` + `shr esi,8` + `xor esi,[table+rdx*4]`
- 变体: CRC32C（Castagnoli 0x1EDC6F41）；MPEG2（初始 0xFFFFFFFF，输出不取反）

### Adler-32 / Fletcher
- Adler-32: 两个 16 位累加器（a=1, b=0），每字节 `a+=byte; b+=a; a %= 65521`——常量 65521 (0xFFF1) 是特征
- Fletcher-32: 无素数取模，模 65535

## 哈希

| 算法 | 特征常量/结构 |
|------|--------------|
| djb2 | 初始 5381，每字符 `hash = hash*33 + c`（`lea rax,[rax+rax*8]` 出现 3 次可组 *33） |
| FNV-1a | 偏移 0x811C9DC5，质数 0x01000193，逐字节 XOR 后乘 |
| MurmurHash | 常数 0x5BD1E995（x86）等，混合旋转模式 `ror` |
| xxHash | 大素数常数（0x9E3779B1 等）逐字混合 |
| MD5/SHA-1/SHA-2 | 固定初始 IV 常量表（十六进制魔数），特征明显 |
| SipHash | 0x736F6D6570736575 等 8 字节常量 |

## 加密

### XOR
- 单字节: 全局常量 key 循环 XOR（key 常 0xAA/0x55/0xFF）
- 多字节/流: 长度与数据相同的 key 表或 key 轮转（`inc` + 与 keylen 比较）
- 识别: 异或指令 `xor [reg+idx], imm/reg` + 循环

### TEA/XTEA
- delta 常量 `0x9E3779B9`，32 轮（XTEA 由 sum 调度），位移 4/5 组合
- 特征: 两次 `add/shift/xor` 块结构

### RC4
- S 盒初始化: 0-255 填表 + 双重交换循环（KSA）；然后 PRGA 交换
- 特征: 256 字节栈/堆数组 + 交换（`xchg`）循环

### AES
- 256 字节 S-box（静态表，常数 `0x63` 起始序列）+ MixColumns 常量 `0x1B/0x02/0x03`；或 T-table 变体（4×256×4 字节大表）
- 识别: 大静态表 + `shift` 组合；round key 扩展循环

### ChaCha20/Salsa20
- 常量 `expand 32-byte k`（0x61707865, 0x3320646E, 0x79622D32, 0x6B206574）+ 四分之一轮（add/xor/rotl 模式）

## 编码

- **Base64**: 64 字符表 + 移位组合（`shr/shl` 6 位重组），特征 `0x3F` 掩码
- **Base58**: 58 字符表（比特币等），常量无 `0`/`O`/`I`/`l`
- **URL-safe Base64**: 表内 `+`/`/` 换 `-`/`_`
- **Hex**: 半字节移位 + 0x30/0x37 调整

## 压缩

- LZ 系: 长度-距离对（`match` 引用），滑动窗口
- deflate/zlib: 哈夫曼表重建 + LZ77；特征 0x78 0x9C 等 zlib 头
- LZ4: 令牌字节（高 4 位字面量长/低 4 位匹配长）
- 熵编码后出现大量位操作 + 位缓冲（bitstream）读取模式

## 识别方法论

1. 查常量表: 搜索魔数（0x9E3779B9、0xEDB88320、5381、0x811C9DC5、MD5 IV）
2. 查结构: 256 项表→CRC/S盒；64 项表→Base64；大 4KB 表→AES T-table
3. 查运算模式: 移位+异或组合→哈希/校验；add+rotate→流加密
4. 确认后立即写入 knowledge/discovered/algorithm-fingerprints.md（core.knowledge）
