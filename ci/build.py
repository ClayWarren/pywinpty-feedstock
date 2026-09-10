import hashlib,json,os,struct,subprocess,sys,tempfile
from pathlib import Path
from conda_package_handling.api import extract
subdir='win-arm64'
os.environ.update(CONDA_SUBDIR=subdir,CONDA_SOLVER='libmamba',CONDA_CHANNEL_PRIORITY='strict')
local=Path('C:/pywinpty-local')
conda=[sys.executable,'C:/pywinpty-tools/Scripts/conda-script.py']
def run(args):
    print(subprocess.list2cmdline([str(x) for x in args]),flush=True)
    subprocess.run(args,check=True)
run(conda+['index',str(local)])
for name in ['winpty']:
    root=Path('ci/prerequisites')/name
    print((root/'source.json').read_text(),flush=True)
    run(conda+['build',str(root/'recipe'),'-m',str(root/'variant.yaml'),'--variants',json.dumps({'build_platform':subdir}),'--croot','C:/pywinpty-build','--output-folder',str(local),'--no-anaconda-upload','--override-channels','-c','file:///C:/pywinpty-local','-c','conda-forge'])
    run(conda+['index',str(local)])
run(conda+['build','recipe','-m','.ci_support/win_arm64_python3.14.____cp314.yaml','--variants',json.dumps({'build_platform':subdir}),'--croot','C:/pywinpty-build','--output-folder',str(local),'--no-anaconda-upload','--override-channels','-c','file:///C:/pywinpty-local','-c','conda-forge'])
manifest=[]
for p in sorted((local/subdir).glob('*.conda')):
    with tempfile.TemporaryDirectory() as td:
        extract(str(p),dest_dir=td)
        idx=json.loads((Path(td)/'info/index.json').read_text())
        assert idx['subdir']==subdir,idx
        for dll in Path(td).rglob('*.dll'):
            b=dll.read_bytes(); off=struct.unpack_from('<I',b,60)[0]
            assert b[off:off+4]==b'PE\0\0'
            assert struct.unpack_from('<H',b,off+4)[0]==0xaa64,dll
            print('AA64 verified:',dll.relative_to(td),flush=True)
    manifest.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(local/subdir/'sha256.json').write_text(json.dumps(manifest,indent=2))
print('PASS: winpty prerequisite and pywinpty installed backend tests on native ARM64',flush=True)
