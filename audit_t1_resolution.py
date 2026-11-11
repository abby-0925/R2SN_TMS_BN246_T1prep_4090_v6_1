#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast header-only T1 spatial-resolution audit for TMS subjects; no data copies."""
import argparse,csv
from collections import Counter
from pathlib import Path
import nibabel as nib
import numpy as np


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',default='/data02/tanghui/TMS-MRI/R2SN_BN246_lesionaware_v2/00_manifest/manifest_TMS_ses01.csv')
    p.add_argument('--out',default='/data02/tanghui/TMS-MRI/R2SN_BN246_lesionaware_v2/00_manifest/T1_resolution_QC.csv')
    p.add_argument('--threshold-mm',type=float,default=3.0)
    a=p.parse_args();counts=Counter();rows=[]
    for r in csv.DictReader(open(a.manifest,encoding='utf-8-sig',newline='')):
        z=dict(id=r['id'],code=r['code'],t1=r['t1'])
        try:
            im=nib.load(r['t1']);shape=im.shape[:3];v=np.asarray(im.header.get_zooms()[:3],dtype=float)
            z.update(shape_x=shape[0],shape_y=shape[1],shape_z=shape[2],
                     vx_mm=float(v[0]),vy_mm=float(v[1]),vz_mm=float(v[2]),
                     max_voxel_mm=float(v.max()),orientation=''.join(nib.aff2axcodes(im.affine)),
                     status='THICK_T1_REVIEW' if v.max()>a.threshold_mm else 'VOXEL_SIZE_PASS')
        except Exception as exc:z['status']='HEADER_ERROR';z['error']=str(exc)
        rows.append(z);counts[z['status']]+=1
    dest=Path(a.out);dest.parent.mkdir(exist_ok=True,parents=True)
    keys=['id','code','t1','shape_x','shape_y','shape_z','vx_mm','vy_mm','vz_mm','max_voxel_mm','orientation','status','error']
    with dest.open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(rows)
    print('TOTAL',len(rows),'COUNTS',dict(counts),'CSV',dest)

if __name__=='__main__':main()
