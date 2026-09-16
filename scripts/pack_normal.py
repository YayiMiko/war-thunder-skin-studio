"""Pack baked smoothness/metal/paint-mask controls; preserve original G/A pixels."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

def pack(source,controls,output):
    original=np.array(Image.open(source).convert('RGBA'));c=np.load(controls,allow_pickle=False)
    if c.ndim!=3 or c.shape[:2]!=original.shape[:2] or c.shape[2]<3:raise ValueError('Controls must match original normal H/W and contain smoothness, metalness, mask.')
    if not np.isfinite(c).all():raise ValueError('Controls contain NaN/Inf')
    c=np.flipud(c).clip(0,1);mask=c[:,:,2]>0
    result=original.copy()
    # The shader already blended partial paint coverage. Do not blend it twice.
    for dst,src in [(0,0),(2,1)]:result[:,:,dst]=np.where(mask,np.rint(c[:,:,src]*255),original[:,:,dst]).astype('uint8')
    assert np.array_equal(original[:,:,[1,3]],result[:,:,[1,3]])
    Path(output).parent.mkdir(parents=True,exist_ok=True);Image.fromarray(result).save(output)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('controls');p.add_argument('output');a=p.parse_args();pack(a.source,a.controls,a.output)
