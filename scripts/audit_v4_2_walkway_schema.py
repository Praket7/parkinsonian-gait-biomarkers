#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from check_v4_2_freeze import check
from src.v4_2.walkway_schema import audit
def main():
 p=argparse.ArgumentParser();p.add_argument('--v1',required=True);p.add_argument('--longitudinal',required=True);p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check(): raise SystemExit('\n'.join(check()))
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);out.joinpath('walkway_schema_audit.json').write_text(json.dumps({'v1':audit(Path(a.v1)),'longitudinal':audit(Path(a.longitudinal))},indent=2)+'\n')
if __name__=='__main__':main()
