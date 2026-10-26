"""Validate native Picture tags; never infer graph connectivity."""

import argparse

import json

import re

from pathlib import Path



def validate(prompt, provided, connected=None):

    if provided < 0 or (connected is not None and connected < 0):

        raise ValueError('Media counts must be nonnegative')

    tags=sorted({int(n) for n in re.findall(r'<Picture\s+(\d+)\s*>',prompt,re.I)})

    errors=[]

    for n in tags:

        if n < 1: errors.append(f'Picture {n}: ordinal starts at 1')

        if n > provided: errors.append(f'Picture {n}: only {provided} logically supplied pictures')

        if connected is not None and n > connected:

            errors.append(f'Picture {n}: only {connected} confirmed connected pictures')

    if re.findall(r'@图片\s*\d+',prompt):

        errors.append('Legacy aliases present; use this app documented syntax first')

    return {'ok':not errors,'pictureTags':tags,'errors':errors,'connectionVerified':connected is not None,'scope':'Native Picture ordinal preflight only'}



def main():

    p=argparse.ArgumentParser(description=__doc__)

    p.add_argument('prompt_file',type=Path)

    p.add_argument('--provided-pictures',type=int,required=True)

    p.add_argument('--connected-pictures',type=int)

    a=p.parse_args()

    result=validate(a.prompt_file.read_text('utf-8-sig'),a.provided_pictures,a.connected_pictures)

    print(json.dumps(result,ensure_ascii=False,indent=2))

    raise SystemExit(0 if result['ok'] else 2)



if __name__=='__main__': main()

