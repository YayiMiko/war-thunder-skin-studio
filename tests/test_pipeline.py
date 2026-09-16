import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pack_normal import pack
from studio import write,make_blk,validate_package,main,identifier,inside,digest

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.original=np.arange(64,dtype=np.uint8).reshape(4,4,4)
        Image.fromarray(self.original).save(self.p/'source.png')
    def tearDown(self):self.tmp.cleanup()
    def test_packing_preserves_normal_and_orientation(self):
        c=np.zeros((4,4,4),dtype=np.float32);c[0,0]=[.6,.25,.5,1]
        np.save(self.p/'c.npy',c);result=pack(self.p/'source.png',self.p/'c.npy',self.p/'n.tga')
        np.testing.assert_array_equal(result[:,:,[1,3]],self.original[:,:,[1,3]])
        self.assertEqual(int(result[-1,0,0]),153);self.assertEqual(int(result[-1,0,2]),64)
        np.testing.assert_array_equal(result[0,0],self.original[0,0])
    def test_reject_invalid_controls(self):
        for c in [np.zeros((2,2,4)),np.full((4,4,4),np.nan)]:
            np.save(self.p/'c.npy',c)
            with self.assertRaises(ValueError):pack(self.p/'source.png',self.p/'c.npy',self.p/'n.tga')
    def package(self):
        Image.fromarray(self.original).convert('RGB').save(self.p/'jet_c.tga')
        Image.fromarray(self.original).save(self.p/'jet_n.tga')
        entries=[{'file':'jet_c.tga','from':'jet_c*','role':'color'}, {'file':'jet_n.tga','from':'jet_n*','role':'normal','normal_source':'source.png'}]
        write(self.p/'package.json',{'vehicle':'jet','textures':entries})
        (self.p/'jet.blk').write_text(make_blk([(x['from'],x['file']) for x in entries]),encoding='utf-8')
    def test_validate_and_reject_normal_mutation(self):
        self.package();self.assertTrue(validate_package(self.p)['ok'])
        a=self.original.copy();a[1,1,3]+=1;Image.fromarray(a).save(self.p/'jet_n.tga')
        with self.assertRaisesRegex(ValueError,'G/A'):validate_package(self.p)
    def test_actual_format_must_match_extension(self):
        self.package();Image.fromarray(self.original).save(self.p/'jet_n.tga',format='PNG')
        with self.assertRaisesRegex(ValueError,'mismatch'):validate_package(self.p)
    def test_install_no_overwrite(self):
        self.package();game=self.p/'fake-game';game.mkdir();cfg=self.p/'env.json'
        write(cfg,{'library':str(self.p/'library'),'game_root':str(game),'blender':sys.executable})
        args=['--config',str(cfg),'install',str(self.p),'--skin-name','sample']
        main(args);before=digest(game/'UserSkins/sample/jet_n.tga')
        with self.assertRaises(FileExistsError):main(args)
        self.assertEqual(before,digest(game/'UserSkins/sample/jet_n.tga'))
    def test_paths_and_black_source(self):
        with self.assertRaises(ValueError):identifier('../bad')
        with self.assertRaises(ValueError):inside(self.p,'../bad')
        self.package();Image.new('RGB',(4,4)).save(self.p/'jet_c.tga')
        with self.assertRaisesRegex(ValueError,'Uniform'):validate_package(self.p)
    def test_new_order_preserves_art_and_requires_choice(self):
        lib=self.p/'library';write(lib/'vehicles/jet/vehicle.json',{'id':'jet'})
        cfg=self.p/'env.json';write(cfg,{'library':str(lib),'game_root':str(self.p),'blender':sys.executable})
        main(['--config',str(cfg),'new-order','--vehicle','jet','--id','test','--art',str(self.p/'source.png'),'--theme','test'])
        self.assertEqual(digest(self.p/'source.png'),digest(lib/'orders/test/assets/source.png'))
        with self.assertRaisesRegex(ValueError,'selected concept'):
            main(['--config',str(cfg),'bake','--order','test','--out',str(self.p/'unused')])
        self.assertFalse((self.p/'unused').exists())

if __name__=='__main__':unittest.main()
