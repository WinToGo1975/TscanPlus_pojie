#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TscanPlus 一键破解 — 只需这一个文件
====================================
用法: python TscanPlus_Full.py <TscanPlus.exe>
效果: 打开即永久 VIP
"""
import sys, os, struct, shutil, subprocess, tempfile

def patch(exe_path):
    print(f"[*] {exe_path}")
    data = open(exe_path, "rb").read()

    # UPX 自动脱壳
    if b"UPX!" in data[:4096]:
        print("[*] UPX 脱壳...")
        upx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upx.exe")
        if not os.path.exists(upx):
            print("[!] 需要同目录 upx.exe")
            return False
        tmp = tempfile.mktemp(suffix=".exe", dir=os.path.dirname(exe_path))
        shutil.copy2(exe_path, tmp)
        r = subprocess.run([upx, "-d", tmp], capture_output=True, timeout=120)
        if r.returncode != 0:
            print(f"[!] 脱壳失败")
            return False
        data = open(tmp, "rb").read()
        os.remove(tmp)
        print(f"[*] 脱壳完成 ({len(data)//1024//1024} MB)")

    # PE 解析
    pe_off = struct.unpack_from("<I", data, 0x3c)[0]
    imgbase = struct.unpack_from("<Q", data, pe_off+24+24)[0]
    nsec = struct.unpack_from("<H", data, pe_off+6)[0]
    opt_size = struct.unpack_from("<H", data, pe_off+20)[0]
    sec_off = pe_off + 24 + opt_size
    secs = []
    for i in range(nsec):
        s = data[sec_off+i*40: sec_off+i*40+40]
        secs.append((int.from_bytes(s[12:16],"little"),
                     int.from_bytes(s[20:24],"little"),
                     int.from_bytes(s[16:20],"little")))

    def va2off(va):
        rva = va - imgbase
        for vaddr, raddr, rsize in secs:
            if vaddr <= rva < vaddr + rsize:
                return rva - vaddr + raddr
        return None

    # 找 Go pclntab
    pos = data.find(b"\xf1\xff\xff\xff\x00\x00\x01\x08")
    if pos == -1:
        print("[!] 不是 Go 程序")
        return False
    nfunc = struct.unpack_from("<Q", data, pos+8)[0]
    textStart = struct.unpack_from("<Q", data, pos+24)[0]
    funcnameOff = struct.unpack_from("<Q", data, pos+32)[0]
    pclnOff = struct.unpack_from("<Q", data, pos+64)[0]
    ftab = pos + pclnOff
    nametab = pos + funcnameOff

    # 找目标函数
    targets = {"TscanGui/conf.UpInY2UYR": None, "TscanGui/conf.IoxJab0E6": None}
    for i in range(nfunc):
        entryoff, funcoff = struct.unpack_from("<II", data, ftab + i*8)
        try:
            eo, nameoff = struct.unpack_from("<Ii", data, ftab + funcoff)
            npos = nametab + nameoff
            end = data.find(b"\x00", npos)
            name = data[npos:end].decode("utf-8","replace")
            if name in targets:
                targets[name] = textStart + entryoff
        except Exception:
            continue

    if not all(targets.values()):
        print("[!] 找不到目标函数")
        return False

    data = bytearray(data)
    count = 0
    for name, va in targets.items():
        off = va2off(va)
        if off is None:
            continue
        orig = bytes(data[off:off+4])
        if orig == b"\xb0\x01\xc3\x90":
            print(f"[*] {name.split('.')[-1]}: 已 patch")
            count += 1
            continue
        data[off:off+4] = b"\xb0\x01\xc3\x90"
        print(f"[*] {name.split('.')[-1]}: {orig.hex(' ')} → MOV AL,1; RET")
        count += 1

    if count == 0:
        print("[!] 没有 patch")
        return False

    # 备份 + 写回
    bak = exe_path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(exe_path, bak)
        print(f"[*] 备份: {bak}")

    out = exe_path + ".patched"
    open(out, "wb").write(bytes(data))

    if os.path.exists(exe_path):
        os.remove(exe_path)

    was_upx = b"UPX!" in open(bak, "rb").read()[:4096]
    if was_upx:
        upx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upx.exe")
        if not os.path.exists(upx):
            upx = "upx"
        r = subprocess.run([upx, "--best", "-o", exe_path, out],
                          capture_output=True, timeout=300)
        if os.path.exists(exe_path) and r.returncode == 0:
            os.remove(out)
            print(f"[*] 已压缩写回: {exe_path}")
        else:
            shutil.copy2(out, exe_path)
            os.remove(out)
            print(f"[*] 写回(未压缩): {exe_path}")
    else:
        shutil.copy2(out, exe_path)
        os.remove(out)
        print(f"[*] 写回: {exe_path}")

    print(f"\n[OK] 完成! 运行 {exe_path} 即永久 VIP")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python TscanPlus_Full.py <TscanPlus.exe>")
        sys.exit(1)
    sys.exit(0 if patch(sys.argv[1]) else 1)

