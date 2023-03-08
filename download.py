from os import path, makedirs, getcwd, chdir
from argparse import ArgumentParser
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)

p = ArgumentParser("Download LLaMA")
p.add_argument('--check-only', '-c', action='store_true', help="Only doing File")
p.add_argument('--dryrun', '-d', action='store_true', help="Dryrun, only print but no execute")
p.add_argument('--target', '-o', default='downloads', type=str, help="Target output diretory")
p.add_argument('--models', '-m', default=["7B","13B","30B","65B"], nargs='+', help="Models you want to download")
args = p.parse_args()

N_SHARD_DICT = {}
N_SHARD_DICT["7B"] = 0
N_SHARD_DICT["13B"] = 1
N_SHARD_DICT["30B"] = 3
N_SHARD_DICT["65B"] = 7

assert [m in ["7B","13B","30B","65B"] for m in args.models]
TARGET_FOLDER=lambda x: path.join(args.target, x)
PRESIGNED_URL=lambda x: f"https://dobf1k6cxlizq.cloudfront.net/{x}?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9kb2JmMWs2Y3hsaXpxLmNsb3VkZnJvbnQubmV0LyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2NzgzNzAzNzR9fX1dfQ__&Signature=U~QwYCuvk3aDiUWh8n4WjU~ha4dbuJRPsCsC~4jmVjikKKBADxwg5kHBFLLGjnP7jmoJnO9kEHgo5OLDrSBx9l7CauY7qYoIEgar0oR7N~vAPmglIOMCms-F3onBD75bkpXdzbcC7bSuXvwylmWh7cx75Gtbxayl~RgsQFKEh6136hjhLaZoOd9C37eHbjT9t4v3xzX65HZROqO~MGXNIyMYe~~eVA04qMecnhALcgvSKZ5xkcXHFLCTQo583sAJIEgP3BzLWsm0FWPVksm9V~RlbGTck-DNv1BlSRTftBts7VmlU7uWQMuDVLRjxUfOizAjeiDKntd3OmrTdhJ~Xg__&Key-Pair-Id=K231VYXPC1TA1R"

makedirs(TARGET_FOLDER(""), exist_ok=True)

models = ['tokenizer.model', "tokenizer_checklist.chk"]
for s in args.models:
    makedirs(TARGET_FOLDER(s), exist_ok=True)
    models.extend([f"{s}/consolidated.0{n}.pth" for n in range(N_SHARD_DICT[s]+1)])
    models.extend([f"{s}/{f}" for f in ["params.json", "checklist.chk"]])

for i, n in enumerate(models):
    logging.info(f"[{i}/{len(models)}]Downloding {n}...")
    wget_str = f"wget -c {PRESIGNED_URL(n)} -O {TARGET_FOLDER(n)}"
    if args.dryrun:
        logging.debug(f"-- {wget_str}")
    else:
        if not args.check_only:
            subprocess.run(wget_str.split(' '))


for i, s in enumerate(args.models):
    cmd = "md5sum -c checklist.chk"
    logging.info(f"[{i}/{len(args.models)}] Checking Model {s}...")
    if args.dryrun:
        logging.debug(f"-- {cmd}")
    else:
        subprocess.run(cmd.split(' '), cwd=TARGET_FOLDER(s))