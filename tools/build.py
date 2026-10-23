"""Validate and build portable skill bundles. Standard library only; not a writing runtime."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'shuangchuang-wechat'
VERSION = re.search(r'^  version: "([^"]+)"$', (ROOT/'SKILL.md').read_text(encoding='utf-8'), re.M).group(1)


def source_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(x in {'.git', 'dist', '__pycache__', '.github'} for x in p.relative_to(ROOT).parts)
                  and p.suffix != '.pyc')


def workbuddy_entry(text):
    header, body = text.split('\n---\n', 1)
    fields = f'''display_name: "双创团队公众号"
description_zh: "为双创团队写正式自然的公众号推文，突出贡献、减少防御，并支持轻清理与全文重写。"
description_en: "Write innovation-team WeChat articles with evidence-led value narratives, less defensive framing, and scoped Chinese editing."
version: "{VERSION}"
author: "mzxuan08"
'''
    return header + '\n' + fields + '---\n' + body


def validate(files):
    entry=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    assert entry.startswith('---\n')
    header, body=entry[4:].split('\n---\n',1)
    assert re.search(r'^name: '+NAME+r'$',header,re.M)
    assert re.search(r'^description: .+',header,re.M)
    assert len(list(ROOT.rglob('SKILL.md')))==1, 'More than one skill entry'
    links=0
    for p in files:
        if p.suffix not in {'.md','.json','.yaml','.py'}:
            continue
        text=p.read_text(encoding='utf-8')
        if p.suffix != '.py':
            assert not re.search(r'[A-Za-z]:[\\/](?:Users|Download)',text), f'Personal path: {p}'
            assert 'Ming的电脑' not in text, f'Personal machine name: {p}'
        if p.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' in link or link.startswith('#'):
                    continue
                target=(p.parent/link.split('#')[0]).resolve()
                target.relative_to(ROOT)
                assert target.is_file(),f'Broken local link {p}: {link}'
                links+=1
    provenance=json.loads((ROOT/'references/upstream/provenance.json').read_text(encoding='utf-8'))
    for rec in provenance['files']:
        target=ROOT/'references/upstream'/rec['snapshot']
        assert hashlib.sha256(target.read_bytes()).hexdigest()==rec['snapshot_sha256']
        assert not Path(rec['source']).is_absolute()
    adapted=provenance['adapted_principles']
    target=(ROOT/'references/upstream'/adapted['adaptation']).resolve()
    assert hashlib.sha256(target.read_bytes()).hexdigest()==adapted['adaptation_sha256']
    cards=(ROOT/'references/source-cards.md').read_text(encoding='utf-8')
    assert all(f'## S{i}｜' in cards for i in range(1,7))
    corpus=json.loads((ROOT/'references/learning-corpus.json').read_text(encoding='utf-8'))
    new_cards=(ROOT/'references/expanded-sources.md').read_text(encoding='utf-8')
    articles=corpus['articles']
    assert len(articles)==corpus['new_sample_count']
    assert len({x['id'] for x in articles})==len(articles)
    assert len({x['url'] for x in articles})==len(articles)
    assert all(f"## {x['id']}｜" in new_cards for x in articles)
    assert corpus['sample_count_total']==6+len(articles)
    assert [x['id'] for x in articles]==[f'N{i:02d}' for i in range(1,len(articles)+1)]
    assert all(x['url'].startswith('https://') and x['reading'] for x in articles)
    batch_ids=[item for batch in corpus['batches'] for item in batch['article_ids']]
    assert batch_ids==[x['id'] for x in articles], 'Batch index differs from source cards'
    assert corpus['batches'][-1]['version']==VERSION
    adapted_entry=workbuddy_entry(entry)
    wb_header,wb_body=adapted_entry[4:].split('\n---\n',1)
    assert wb_body==body
    for key in ('name','description','description_zh','description_en','version','author'):
        assert re.search(r'^'+key+r': .+',wb_header,re.M)
    assert f'version: "{VERSION}"' in wb_header
    return dict(version=VERSION,files=len(files),local_links=links,original_source_cards=6,new_source_cards=len(articles),latest_batch_source_cards=len(corpus['batches'][-1]['article_ids']),source_cards_total=corpus['sample_count_total'],upstream_snapshots=len(provenance['files']),single_entry=True,portable_paths=True,workbuddy_metadata=True,writing_body_identical=True)


def package(files,out,workbuddy=False):
    filename=NAME+('-workbuddy' if workbuddy else '')+'.zip'
    path=out/filename
    payload={p.relative_to(ROOT).as_posix():p.read_bytes() for p in files}
    if workbuddy:
        payload['SKILL.md']=workbuddy_entry(payload['SKILL.md'].decode('utf-8')).encode('utf-8')
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in payload.items():
            item=zipfile.ZipInfo(NAME+'/'+name,date_time=(2026,10,23,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED
            item.external_attr=0o100644 << 16
            archive.writestr(item,data)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(payload)
        for name,data in payload.items():
            assert archive.read(NAME+'/'+name)==data
    return dict(name=filename,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'dist')
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    files=source_files()
    report=validate(files)
    if not args.check_only:
        args.out.mkdir(parents=True,exist_ok=True)
        assets=[package(files,args.out,False),package(files,args.out,True)]
        (args.out/'SHA256SUMS.txt').write_text(''.join(f"{x['sha256']}  {x['name']}\n" for x in assets),encoding='utf-8')
        report['assets']=assets
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
