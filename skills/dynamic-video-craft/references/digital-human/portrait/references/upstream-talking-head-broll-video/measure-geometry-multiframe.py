# -*- coding: utf-8 -*-
"""FULL 布局边界 + 汇总 SPLIT/FULL 全部几何"""
import io, sys, subprocess, numpy as np
sys.stdout = io.TextIOWrapper(open('_geom2.log', 'wb'), encoding='utf-8', write_through=True)
SRC='下载.mp4'; W,H=1280,720

def frame(t):
    p=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',SRC,'-frames:v','1',
        '-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True)
    if len(p.stdout)<W*H*3: return None
    return np.frombuffer(p.stdout[:W*H*3],np.uint8).reshape(H,W,3)

def edges_h(g, y, lo, hi):
    """在 [lo,hi) 横向找黑线(<=40)位置"""
    seg=g[y][lo:hi]; d=np.where(seg<=40)[0]
    return [lo+int(i) for i in d]

def edges_v(g, x, lo, hi):
    seg=g[lo:hi, x]; d=np.where(seg<=40)[0]
    return [lo+int(i) for i in d]

# _m3.log 布局节奏里的 FULL 段
FULL_TS=[3, 8, 20, 26, 40, 52, 70, 96, 115, 145, 172, 200, 225, 250]
print('='*78); print('FULL 布局边界（找 B 框黑线四边）'); print('='*78)
stat={'L':[], 'R':[], 'T':[], 'B':[]}
for t in FULL_TS:
    im=frame(t)
    if im is None: continue
    g=im.mean(axis=2)
    L=edges_h(g,360,0,120); R=edges_h(g,360,1160,1280)
    T=edges_v(g,640,0,90);   B=edges_v(g,640,600,700)
    # 只要四边都检出唯一黑线簇才算标准 FULL
    if L and R and T and B:
        l,r,tp,bt=min(L),max(R),min(T),max(B)
        # 排除 SPLIT（左黑线应在 x<60）
        if l<60:
            stat['L'].append(l); stat['R'].append(r); stat['T'].append(tp); stat['B'].append(bt)
            print(f'  t={t:3d}s  L={l:4d} R={r:4d} T={tp:3d} B={bt:3d}  → 宽{r-l+1} 高{bt-tp+1} 距底{720-bt-1}')
        else:
            print(f'  t={t:3d}s  非 FULL (左黑线 x={l})')
    else:
        print(f'  t={t:3d}s  边界不全 L={bool(L)} R={bool(R)} T={bool(T)} B={bool(B)}')

print('\n  众数汇总:')
for k,v in stat.items():
    if v: print(f'    {k}: 众数={max(set(v),key=v.count)}  取值={sorted(set(v))}')

print('\n'+'='*78)
print('SPLIT 汇总（基准 t=62s 已测，此处多帧复核四边）')
print('='*78)
sp={'aL':[], 'aR':[], 'aT':[], 'aB':[], 'bL':[], 'bR':[], 'bT':[], 'bB':[]}
for t in (14,16,32,62,104,120,205):
    im=frame(t)
    if im is None: continue
    g=im.mean(axis=2); r=g[300]
    # A 白边：左缘 = 前 40px 内第一个 >=240；右缘 = 380..420 内最后一个 >=240
    w1=np.where(r[0:40]>=240)[0];  aL=int(w1.min()) if len(w1) else None
    w2=np.where(r[380:420]>=240)[0]; aR=380+int(w2.max()) if len(w2) else None
    # B 黑线：左 420..450 最小；右 1230..1270 最小
    s1=r[420:450]; bL=420+int(np.argmin(s1)); v1=int(s1.min())
    s2=r[1230:1270]; bR=1230+int(np.argmin(s2)); v2=int(s2.min())
    # A 竖向白边 col200
    c=g[:,200]
    t1=np.where(c[20:50]>=240)[0]; aT=20+int(t1.min()) if len(t1) else None
    t2=np.where(c[600:660]>=240)[0]; aB=600+int(t2.max()) if len(t2) else None
    # B 竖向黑线 col800
    c8=g[:,800]
    u1=np.where(c8[25:55]<=40)[0]; bT=25+int(u1.min()) if len(u1) else None
    u2=np.where(c8[595:660]<=40)[0]; bB=595+int(u2.max()) if len(u2) else None
    if v1<40 and v2<40 and None not in (aL,aR,aT,aB,bT,bB):
        for k,val in zip(sp.keys(),[aL,aR,aT,aB,bL,bR,bT,bB]): sp[k].append(val)
        print(f'  t={t:3d}s  A[{aL},{aT}]-[{aR},{aB}]  B[{bL},{bT}]-[{bR},{bB}]  中缝={bL-aR-1}')
    else:
        print(f'  t={t:3d}s  跳过')
print('\n  众数汇总:')
for k,v in sp.items():
    if v: print(f'    {k}: 众数={max(set(v),key=v.count)}  取值={sorted(set(v))}')
print('\n完成')
